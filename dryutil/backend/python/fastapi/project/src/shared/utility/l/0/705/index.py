from typing import Any
from fastapi import Request
from fastapi.responses import JSONResponse
from sqlalchemy import Column, String, Text, DateTime, Integer, func as sa_func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.future import select
import uuid
import httpx
import re
import os
import logging
import json as _json
from datetime import datetime, timezone, timedelta
from collections import defaultdict
from logging.handlers import RotatingFileHandler
from src.shared.utility.u.fake_req_obj.index import fake_req_obj
from src.shared.util.jwt_handler.index import JWTHandler


# ── Logging ────────────────────────────────────────────────────────────────

_log = logging.getLogger("utility_705")
if not _log.handlers:
    _log.setLevel(getattr(logging, os.getenv('LOG_LEVEL', 'INFO').upper(), logging.INFO))
    _h = logging.StreamHandler()
    _h.setFormatter(logging.Formatter('{"time": "%(asctime)s", "level": "%(levelname)s", "msg": "%(message)s"}'))
    _log.addHandler(_h)
    if os.getenv('NODE_ENV') == 'production':
        import sys
        from pathlib import Path
        _lf = os.getenv('LOG_FILE_PATH', '/var/log/instagram_business/app.log')
        Path(_lf).parent.mkdir(parents=True, exist_ok=True)
        _fh = RotatingFileHandler(_lf, maxBytes=10*1024*1024, backupCount=10)
        _fh.setFormatter(_h.formatter)
        _log.addHandler(_fh)


# ── Rate Limiter ───────────────────────────────────────────────────────────

_rate_store: dict = defaultdict(list)
_rate_limit  = int(os.getenv('RATE_LIMIT_PER_MINUTE', '60'))
_rate_enabled = os.getenv('ENABLE_RATE_LIMITING', 'false').lower() == 'true'

def _rate_check(identifier: str) -> bool:
    if not _rate_enabled:
        return True
    now    = datetime.now()
    cutoff = now - timedelta(seconds=60)
    _rate_store[identifier] = [t for t in _rate_store[identifier] if t > cutoff]
    if len(_rate_store[identifier]) >= _rate_limit:
        return False
    _rate_store[identifier].append(now)
    return True

def _rate_id(request: Request) -> str:
    auth = request.headers.get('Authorization', '')
    if auth.startswith('Bearer '):
        return auth[7:50]
    fwd = request.headers.get('X-Forwarded-For')
    if fwd:
        return fwd.split(',')[0].strip()
    return request.client.host if request.client else 'unknown'


# ── Input Validator ────────────────────────────────────────────────────────

def _validate_user_id(user_id: str) -> str:
    if not user_id or not isinstance(user_id, str) or len(user_id) > 255:
        raise Exception("invalid user_id")
    return user_id

def _sanitize(text: str, max_len: int = 1000) -> str:
    if not text:
        return ""
    return str(text).strip().replace('\x00', '')[:max_len]

def _validate_pagination(limit, offset) -> tuple:
    try:
        limit, offset = max(1, min(int(limit or 20), 100)), max(0, int(offset or 0))
    except Exception:
        raise Exception("invalid pagination params")
    return limit, offset


# ── Token Manager ──────────────────────────────────────────────────────────

def _create_access_token(user_id: str, name: str = "") -> str:
    expire_minutes = int(os.getenv('JWT_EXPIRE_MINUTES', '1440'))
    return JWTHandler.create_token(
        {"sub": user_id, "name": name, "security": {"party": ["party_2"]}, "token_type": "access"},
        expire_minutes=expire_minutes
    )

def _create_refresh_token(user_id: str) -> str:
    expire_days = int(os.getenv('JWT_REFRESH_EXPIRE_DAYS', '30'))
    return JWTHandler.create_token(
        {"sub": user_id, "token_type": "refresh", "security": {"party": ["party_2"]}},
        expire_minutes=expire_days * 24 * 60
    )

def _refresh_jwt_if_needed(token: str) -> dict:
    """Return new access token if current one expires within 10 min."""
    try:
        payload = JWTHandler.verify_token(token)
        exp     = payload.get('exp', 0)
        if exp and (exp - datetime.now(timezone.utc).timestamp()) <= 600:
            new_token = _create_access_token(payload.get('sub', ''), payload.get('name', ''))
            return {"refreshed": True, "access_token": new_token}
    except Exception:
        pass
    return {"refreshed": False}


Base = declarative_base()


# ── Core business table ────────────────────────────────────────────────────

class InstagramBusiness(Base):
    """One row per seller — stores Instagram Business config + Meta credentials."""
    __tablename__ = "instagram_business"
    id      = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String(155), nullable=False)
    data    = Column(JSONB, nullable=True)


# ── Shared catalog sync tables (reused from WhatsApp Commerce) ─────────────

class CatalogSyncHistory(Base):
    """One row per full sync run per seller."""
    __tablename__ = "catalog_sync_history"
    id           = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    business_id  = Column(String(155), nullable=False, index=True)
    catalog_id   = Column(String(155), nullable=True)
    status       = Column(String(20), nullable=False, default="running")  # running/completed/partial/failed
    total        = Column(Integer, default=0)
    synced       = Column(Integer, default=0)
    failed       = Column(Integer, default=0)
    started_at   = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime(timezone=True), nullable=True)
    trigger      = Column(String(30), nullable=True, default="manual")    # manual/scheduled/api

class CatalogSyncLog(Base):
    """One row per product per sync run."""
    __tablename__ = "catalog_sync_log"
    id            = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sync_id       = Column(UUID(as_uuid=True), nullable=False, index=True)
    business_id   = Column(String(155), nullable=False, index=True)
    product_id    = Column(String(300), nullable=True)
    product_name  = Column(String(300), nullable=True)
    status        = Column(String(20), nullable=False)   # synced/failed/skipped
    error         = Column(Text, nullable=True)
    meta_response = Column(JSONB, nullable=True)
    created_at    = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


async def index(_p={'data': {'instance': Any}}):

    # ── DB engine setup ────────────────────────────────────────────────────
    _engine = None
    if _p['data'].get('instance') is not None:
        _data        = _p['data']['instance'].data
        _config      = _data.get('config', {}) if isinstance(_data, dict) else {}
        database_url = _config.get('database', {}).get('url')
        if database_url:
            _engine = create_async_engine(database_url, echo=False, future=True)
            async with _engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
                # Create indexes on first run
                await conn.execute(sa_func.text("CREATE INDEX IF NOT EXISTS idx_instagram_business_user_id ON instagram_business(user_id)"))
                await conn.execute(sa_func.text("CREATE INDEX IF NOT EXISTS idx_catalog_sync_history_business_id ON catalog_sync_history(business_id)"))
                await conn.execute(sa_func.text("CREATE INDEX IF NOT EXISTS idx_catalog_sync_history_status ON catalog_sync_history(status)"))
                await conn.execute(sa_func.text("CREATE INDEX IF NOT EXISTS idx_catalog_sync_log_sync_id ON catalog_sync_log(sync_id)"))
                await conn.execute(sa_func.text("CREATE INDEX IF NOT EXISTS idx_catalog_sync_log_business_id ON catalog_sync_log(business_id)"))
                await conn.execute(sa_func.text("CREATE INDEX IF NOT EXISTS idx_catalog_sync_log_status ON catalog_sync_log(status)"))

    # ── Tiny helpers ───────────────────────────────────────────────────────

    def _err(msg, log):
        return JSONResponse(content={"success": False, "message": msg, "data": {"log": log}}, status_code=200)

    def _meta_cfg(row):
        d = row.data or {}
        return d.get('config', {}).get('meta', {})

    async def _get_row(db, body):
        """Find seller row by id or user_id. Auto-creates if not found."""
        if 'id' in body and body['id']:
            result = await db.execute(
                select(InstagramBusiness).where(InstagramBusiness.id == uuid.UUID(body['id']))
            )
            return result.scalar_one_or_none()
        user_id = body.get('user_id', '')
        if not user_id:
            return None
        result = await db.execute(
            select(InstagramBusiness).where(InstagramBusiness.user_id == user_id)
        )
        row = result.scalars().first()
        # Auto-create row on first visit — seller never needs to call 'create' manually
        if not row:
            instance_cfg = {}
            if _p['data'].get('instance') is not None:
                _inst_data = _p['data']['instance'].data or {}
                instance_cfg = _inst_data.get('config', {})
            row = InstagramBusiness(
                user_id=user_id,
                data={
                    'config': {
                        'database':          instance_cfg.get('database', {}),
                        'product_dir_token': instance_cfg.get('product_dir_token', ''),
                        'base_url':          instance_cfg.get('base_url', 'http://localhost:8000'),
                        'meta_app_id':       instance_cfg.get('meta_app_id', ''),
                        'meta_app_secret':   instance_cfg.get('meta_app_secret', ''),
                        'oauth_redirect_uri':instance_cfg.get('oauth_redirect_uri', ''),
                        'meta': {
                            'access_token': '',
                            'instagram_business_account_id': '',
                            'instagram_username': '',
                            'fb_page_id': '',
                            'fb_page_name': '',
                            'catalog_id': '',
                        }
                    },
                    'profile': {'title': ''}
                }
            )
            db.add(row)
            await db.commit()
            await db.refresh(row)
            _log.info(f"[705] auto-created instagram_business row for user_id={user_id}")
        return row

    async def _get_first_business_row(db):
        result = await db.execute(select(InstagramBusiness).limit(1))
        return result.scalar_one_or_none()

    # ── Token management (reused) ──────────────────────────────────────────

    async def _refresh_token_if_needed(token: str, app_id: str, app_secret: str) -> str:
        """Check token expiry and refresh if expiring within 7 days."""
        if not token or not app_id or not app_secret:
            return token
        try:
            async with httpx.AsyncClient() as client:
                r = await client.get(
                    "https://graph.facebook.com/v19.0/debug_token",
                    params={"input_token": token, "access_token": f"{app_id}|{app_secret}"},
                    timeout=10
                )
                data       = r.json().get("data", {})
                expires_at = data.get("expires_at", 0)
                if expires_at == 0:
                    return token  # never-expiring system token
                now_ts    = datetime.now(timezone.utc).timestamp()
                days_left = (expires_at - now_ts) / 86400
                if days_left > 7:
                    return token
                r2 = await client.get(
                    "https://graph.facebook.com/v19.0/oauth/access_token",
                    params={
                        "grant_type":        "fb_exchange_token",
                        "client_id":         app_id,
                        "client_secret":     app_secret,
                        "fb_exchange_token": token,
                    },
                    timeout=10
                )
                new_token = r2.json().get("access_token", token)
                print(f"[token_refresh] refreshed, days_left_was={days_left:.1f}")
                return new_token
        except Exception as e:
            print(f"[token_refresh] failed: {e}")
            return token

    # ── Catalog sync helpers (reused, platform-agnostic) ──────────────────

    def _normalize_product(doc: dict) -> dict:
        """Convert OMS product_dir format → Meta Catalog API payload."""
        price_raw = doc.get('variant_mrp') or doc.get('variant_prices') or doc.get('price', 0)
        if isinstance(price_raw, list):
            price_raw = price_raw[0] if price_raw else 0
        try:
            price_cents = int(float(str(price_raw).replace(',', '').strip()) * 100)
        except Exception:
            price_cents = 0
        retailer_id = str(doc.get('id', doc.get('slug', '')))
        name        = str(doc.get('title', doc.get('name', '')))[:100]
        description = str(doc.get('description', name))[:200] or name
        # extract image from metadata.color[].image[]
        image_url = ''
        metadata  = doc.get('metadata', {})
        colors    = metadata.get('color', metadata.get('colors', []))
        for color in colors:
            images = color.get('image', [])
            parts  = [img.get('url', '') if isinstance(img, dict) else str(img) for img in images]
            base   = next((p for p in parts if p.startswith('https://')), '')
            ext    = next((p for p in parts if any(p.endswith(e) for e in ['.jpg', '.jpeg', '.png', '.webp'])), '')
            if base and ext:
                image_url = base + '/' + ext.lstrip('/')
                break
            elif base and '.' in base.split('/')[-1]:
                image_url = base
                break
        if not image_url:
            for img_key in ['image_url', 'image', 'thumbnail', 'photo']:
                val = doc.get(img_key, '')
                if isinstance(val, list) and val:
                    val = val[0]
                if isinstance(val, str) and val.startswith('https://'):
                    image_url = val
                    break
        if not image_url:
            image_url = 'https://placehold.co/400x400/png'
        product_url = doc.get('url', metadata.get('url', 'https://onamoda.in/'))
        return {
            "retailer_id":  retailer_id,
            "name":         name,
            "description":  description,
            "price":        price_cents,
            "currency":     doc.get('currency', metadata.get('variant', [{}])[0].get('currency', 'INR') if metadata.get('variant') else 'INR'),
            "availability": "in stock",
            "url":          product_url,
            "image_url":    image_url,
        }

    async def _meta_push_one(client: httpx.AsyncClient, token: str, catalog_id: str, payload: dict):
        """POST one product to Meta Catalog."""
        r = await client.post(
            f"https://graph.facebook.com/v19.0/{catalog_id}/products",
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            json=payload,
            timeout=15,
        )
        return r.status_code, r.json()

    async def _meta_delete_one(client: httpx.AsyncClient, token: str, catalog_id: str, retailer_id: str):
        """DELETE one product from Meta Catalog by retailer_id."""
        r = await client.delete(
            f"https://graph.facebook.com/v19.0/{catalog_id}/products",
            headers={"Authorization": f"Bearer {token}"},
            params={"retailer_id": retailer_id},
            timeout=15,
        )
        return r.status_code, r.json()

    async def _fetch_products(token: str, base_url: str, q: str = "*", per_page: int = 250):
        """Fetch products from OMS product_dir — public route first, then authenticated."""
        print(f"[fetch_products] base_url={base_url}")
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{base_url}/client-public/api/i/ona/product_dir?typ=get_product_list",
                json={"q": q, "per_page": per_page, "page": 1},
                timeout=30
            )
            if resp.status_code == 404:
                resp = await client.post(
                    f"{base_url}/client/api/i/ona/product_dir?typ=get_product_list",
                    headers={"Authorization": f"Bearer {token}"},
                    json={"q": q, "per_page": per_page, "page": 1},
                    timeout=30
                )
        print(f"[fetch_products] status={resp.status_code} body={resp.text[:300]}")
        return resp.json()

    # ── Instagram-specific asset discovery ────────────────────────────────

    async def _instagram_discover_assets(token: str) -> dict:
        """
        Discover Instagram Business Accounts, Facebook Pages, and Catalogs
        from a user access token obtained via Facebook Login.
        """
        result = {
            "instagram_accounts": [],  # [{id, username, name, page_id}]
            "facebook_pages":     [],  # [{id, name, instagram_business_account}]
            "catalog_list":       [],  # [{id, name}]
            "token_info":         {},
        }
        async with httpx.AsyncClient() as client:
            # 1. token identity
            r = await client.get(
                "https://graph.facebook.com/v19.0/me",
                params={"access_token": token, "fields": "id,name"}
            )
            result["token_info"] = r.json()
            user_id = result["token_info"].get("id", "")

            # 2. Facebook Pages the user manages
            r_pages = await client.get(
                f"https://graph.facebook.com/v19.0/{user_id}/accounts",
                params={
                    "access_token": token,
                    "fields": "id,name,instagram_business_account"
                }
            )
            pages = r_pages.json().get("data", [])
            for page in pages:
                page_id   = page.get("id")
                page_name = page.get("name", "")
                ig_biz    = page.get("instagram_business_account", {})
                ig_id     = ig_biz.get("id", "")

                result["facebook_pages"].append({
                    "id":                           page_id,
                    "name":                         page_name,
                    "instagram_business_account_id": ig_id,
                })

                # 3. enrich Instagram Business Account details
                if ig_id:
                    r_ig = await client.get(
                        f"https://graph.facebook.com/v19.0/{ig_id}",
                        params={
                            "access_token": token,
                            "fields": "id,name,username,profile_picture_url,followers_count"
                        }
                    )
                    ig_data = r_ig.json()
                    result["instagram_accounts"].append({
                        "id":                  ig_id,
                        "username":            ig_data.get("username", ""),
                        "name":                ig_data.get("name", ""),
                        "profile_picture_url": ig_data.get("profile_picture_url", ""),
                        "followers_count":     ig_data.get("followers_count", 0),
                        "page_id":             page_id,
                        "page_name":           page_name,
                    })

            # 4. Catalogs via business manager
            r_biz = await client.get(
                f"https://graph.facebook.com/v19.0/{user_id}/businesses",
                params={"access_token": token, "fields": "id,name,owned_product_catalogs"}
            )
            for biz in r_biz.json().get("data", []):
                biz_id = biz.get("id")
                r_cat  = await client.get(
                    f"https://graph.facebook.com/v19.0/{biz_id}/owned_product_catalogs",
                    params={"access_token": token, "fields": "id,name"}
                )
                for cat in r_cat.json().get("data", []):
                    result["catalog_list"].append({"id": cat.get("id"), "name": cat.get("name", "")})

        return result

    async def _link_catalog_to_instagram_shop(token: str, ig_user_id: str, catalog_id: str):
        """Associate a Meta catalog with an Instagram Shopping account."""
        async with httpx.AsyncClient() as client:
            r = await client.post(
                f"https://graph.facebook.com/v19.0/{ig_user_id}/product_catalogs",
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                json={"catalog_id": catalog_id},
                timeout=15,
            )
        rj = r.json()
        if rj.get('error', {}).get('error_subcode') == 2388099:
            rj = {'success': True, 'note': 'already_linked'}
        print(f"[link_catalog_instagram] result={rj}")
        return rj


    # ── i — main request handler ───────────────────────────────────────────

    async def i(request: Request):
        try:
            if _engine is None:
                raise Exception("database engine not configured")

            # rate limiting
            if not _rate_check(_rate_id(request)):
                return JSONResponse(content={"success": False, "message": "Rate limit exceeded"}, status_code=429)

            try:
                body = await request.json()
            except Exception as je:
                _log.error(f"Failed to parse request body: {je}")
                raise Exception(f"Invalid JSON body: {je}")
            
            typ  = request.query_params.get('typ')
            _log.info(f"[705] typ={typ} user={body.get('user_id', '-')}")
            
            async with AsyncSession(_engine) as db:
                match typ:
                    # ── CRUD ───────────────────────────────────────────────
                    case 'create':
                        row = InstagramBusiness(user_id=body['user_id'], data=body.get('data', {}))
                        db.add(row)
                        await db.commit()
                        await db.refresh(row)
                        return JSONResponse(content={"success": True, "data": {"id": str(row.id)}}, status_code=200)

                    case 'get':
                        result = await db.execute(
                            select(InstagramBusiness).where(InstagramBusiness.id == uuid.UUID(body['id']))
                        )
                        row = result.scalar_one_or_none()
                        if not row:
                            raise Exception("record not found")
                        return JSONResponse(content={"success": True, "data": {
                            "id": str(row.id), "user_id": row.user_id, "data": row.data
                        }}, status_code=200)

                    case 'list':
                        result = await db.execute(
                            select(InstagramBusiness).where(InstagramBusiness.user_id == body['user_id'])
                        )
                        rows = result.scalars().all()
                        return JSONResponse(content={"success": True, "data": [
                            {"id": str(r.id), "data": r.data} for r in rows
                        ]}, status_code=200)

                    case 'update':
                        row = await _get_row(db, body)
                        if not row:
                            row = InstagramBusiness(user_id=body.get('user_id', str(uuid.uuid4())), data=body.get('data', {}))
                            db.add(row)
                        else:
                            if 'data' in body:
                                row.data = body['data']
                        await db.commit()
                        await db.refresh(row)
                        return JSONResponse(content={"success": True, "data": {"id": str(row.id)}}, status_code=200)

                    case 'delete':
                        result = await db.execute(
                            select(InstagramBusiness).where(InstagramBusiness.id == uuid.UUID(body['id']))
                        )
                        row = result.scalar_one_or_none()
                        if not row:
                            raise Exception("record not found")
                        await db.delete(row)
                        await db.commit()
                        return JSONResponse(content={"success": True, "data": {}}, status_code=200)

                    # ── Meta config save ───────────────────────────────────

                    case 'meta_config_save' | 'save_meta_config':
                        row = await _get_row(db, body)
                        if not row:
                            raise Exception("record not found — create first")
                        d   = dict(row.data or {})
                        cfg = dict(d.get('config', {}))
                        if 'meta' in body:
                            meta_payload = body['meta']
                        else:
                            src = body.get('data', {})
                            meta_payload = {
                                'access_token':                  src.get('access_token', ''),
                                'instagram_business_account_id': src.get('instagram_business_account_id', ''),
                                'instagram_username':            src.get('instagram_username', ''),
                                'fb_page_id':                    src.get('fb_page_id', ''),
                                'fb_page_name':                  src.get('fb_page_name', ''),
                                'catalog_id':                    src.get('catalog_id', ''),
                            }
                        cfg['meta'] = meta_payload
                        if body.get('product_dir_token'):
                            cfg['product_dir_token'] = body['product_dir_token']
                        if body.get('base_url'):
                            cfg['base_url'] = body['base_url']
                        d['config'] = cfg
                        row.data    = d
                        await db.commit()
                        return JSONResponse(content={"success": True, "data": {}}, status_code=200)

                    case 'get_meta_config':
                        row = await _get_row(db, body)
                        if not row:
                            raise Exception("record not found")
                        meta  = _meta_cfg(row)
                        token = meta.get('access_token', '')
                        return JSONResponse(content={"success": True, "data": {
                            "instagram_business_account_id": meta.get('instagram_business_account_id', ''),
                            "instagram_username":            meta.get('instagram_username', ''),
                            "fb_page_id":                    meta.get('fb_page_id', ''),
                            "fb_page_name":                  meta.get('fb_page_name', ''),
                            "catalog_id":                    meta.get('catalog_id', ''),
                            "access_token_masked":           token[-6:] if token else '',
                            "access_token_set":              bool(token),
                        }}, status_code=200)

                    # ── OAuth flow (reused architecture) ───────────────────

                    case 'meta_oauth_start':
                        if _engine is None:
                            return JSONResponse(content={"success": False, "message": "Database engine not configured", "data": {}}, status_code=400)
                        row = await _get_row(db, body)
                        if not row:
                            raise Exception("record not found")
                        d   = row.data or {}
                        cfg = d.get('config', {})
                        app_id       = cfg.get('meta_app_id', '') or os.getenv('META_APP_ID', '')
                        redirect_uri = body.get('redirect_uri', cfg.get('oauth_redirect_uri', ''))
                        state        = body.get('state', str(row.id))
                        if not app_id:
                            return JSONResponse(content={"success": False, "message": "META_APP_ID not configured. Set META_APP_ID environment variable or pass meta_app_id in config.", "data": {}}, status_code=400)
                        if not redirect_uri:
                            redirect_uri = 'http://localhost:5173/oauth/callback'
                        scope = (
                            'instagram_basic,'
                            'instagram_content_publish,'
                            'pages_show_list,'
                            'catalog_management,'
                            'commerce_management,'
                            'business_management'
                        )
                        auth_url = (
                            f"https://www.facebook.com/v19.0/dialog/oauth"
                            f"?client_id={app_id}"
                            f"&redirect_uri={redirect_uri}"
                            f"&scope={scope}"
                            f"&state={state}"
                            f"&response_type=code"
                        )
                        return JSONResponse(content={"success": True, "data": {
                            "auth_url": auth_url,
                            "state":    state,
                        }}, status_code=200)

                    case 'meta_oauth_callback':
                        row = await _get_row(db, body)
                        if not row:
                            raise Exception("record not found")
                        d   = dict(row.data or {})
                        cfg = dict(d.get('config', {}))
                        app_id       = cfg.get('meta_app_id', '') or os.getenv('META_APP_ID', '')
                        app_secret   = cfg.get('meta_app_secret', '') or os.getenv('META_APP_SECRET', '')
                        redirect_uri = body.get('redirect_uri', cfg.get('oauth_redirect_uri', ''))
                        code         = body.get('code', '')
                        if not code:
                            raise Exception("authorization code is required")
                        if not app_id or not app_secret:
                            raise Exception("META_APP_ID and META_APP_SECRET not configured. Set environment variables.")

                        # 1. exchange code → short-lived token
                        async with httpx.AsyncClient() as client:
                            r = await client.get(
                                "https://graph.facebook.com/v19.0/oauth/access_token",
                                params={
                                    "client_id":     app_id,
                                    "client_secret": app_secret,
                                    "redirect_uri":  redirect_uri,
                                    "code":          code,
                                },
                                timeout=15
                            )
                        token_data = r.json()
                        if "error" in token_data:
                            raise Exception(f"Token exchange failed: {token_data['error'].get('message')}")
                        short_token = token_data.get("access_token", "")

                        # 2. exchange → long-lived token
                        async with httpx.AsyncClient() as client:
                            r2 = await client.get(
                                "https://graph.facebook.com/v19.0/oauth/access_token",
                                params={
                                    "grant_type":        "fb_exchange_token",
                                    "client_id":         app_id,
                                    "client_secret":     app_secret,
                                    "fb_exchange_token": short_token,
                                },
                                timeout=15
                            )
                        token = r2.json().get("access_token", short_token)

                        # 3. discover Instagram Business + Facebook Page + Catalogs
                        assets = await _instagram_discover_assets(token)

                        # 4. auto-select if only one of each
                        auto_ig_id       = assets["instagram_accounts"][0]["id"]       if len(assets["instagram_accounts"]) == 1 else None
                        auto_ig_username = assets["instagram_accounts"][0]["username"] if len(assets["instagram_accounts"]) == 1 else None
                        auto_page_id     = assets["facebook_pages"][0]["id"]           if len(assets["facebook_pages"]) == 1   else None
                        auto_page_name   = assets["facebook_pages"][0]["name"]         if len(assets["facebook_pages"]) == 1   else None
                        auto_catalog     = assets["catalog_list"][0]["id"]             if len(assets["catalog_list"]) == 1     else None

                        # 5. auto-create catalog if none found
                        if not auto_catalog and auto_ig_id:
                            try:
                                seller_name = (row.data or {}).get('profile', {}).get('title', 'My Store')
                                async with httpx.AsyncClient() as client:
                                    r_biz = await client.get(
                                        f"https://graph.facebook.com/v19.0/me/businesses",
                                        params={"access_token": token, "fields": "id"}
                                    )
                                    biz_id = (r_biz.json().get("data") or [{}])[0].get("id", "")
                                    if biz_id:
                                        rc = await client.post(
                                            f"https://graph.facebook.com/v19.0/{biz_id}/owned_product_catalogs",
                                            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                                            json={"name": f"{seller_name} Catalog"},
                                            timeout=15
                                        )
                                        created = rc.json()
                                        if "id" in created:
                                            auto_catalog = created["id"]
                                            print(f"[oauth_callback] auto-created catalog: {auto_catalog}")
                            except Exception as e:
                                print(f"[oauth_callback] catalog auto-create failed: {e}")

                        # 6. save config
                        existing_meta = cfg.get('meta', {})
                        cfg['meta'] = {
                            **existing_meta,
                            'access_token':                  token,
                            'instagram_business_account_id': auto_ig_id       or existing_meta.get('instagram_business_account_id', ''),
                            'instagram_username':            auto_ig_username  or existing_meta.get('instagram_username', ''),
                            'fb_page_id':                    auto_page_id     or existing_meta.get('fb_page_id', ''),
                            'fb_page_name':                  auto_page_name   or existing_meta.get('fb_page_name', ''),
                            'catalog_id':                    auto_catalog     or existing_meta.get('catalog_id', ''),
                        }
                        cfg['oauth_connected_at'] = datetime.now(timezone.utc).isoformat()
                        d['config'] = cfg
                        row.data    = d
                        await db.commit()

                        # 7. link catalog to Instagram Shop
                        _ig_id      = cfg['meta'].get('instagram_business_account_id', '')
                        _catalog_id = cfg['meta'].get('catalog_id', '')
                        if _ig_id and _catalog_id:
                            try:
                                await _link_catalog_to_instagram_shop(token, _ig_id, _catalog_id)
                            except Exception as e:
                                print(f"[oauth_callback] catalog link warning: {e}")

                        # 8. auto-sync products after OAuth
                        if cfg['meta'].get('catalog_id') and cfg['meta'].get('access_token'):
                            try:
                                pd_token = cfg.get('product_dir_token', '')
                                base_url = cfg.get('base_url', 'https://fastapi.dryutil.1mn.io')
                                pd_resp  = await _fetch_products(pd_token, base_url, per_page=250)
                                products = pd_resp.get('data', {}).get('products',
                                           pd_resp.get('data', {}).get('hits', []))
                                if isinstance(products, dict):
                                    products = products.get('hits', products.get('products', []))
                                if products:
                                    async with httpx.AsyncClient() as _sync_client:
                                        for _p in products:
                                            _doc     = _p.get('document', _p)
                                            _payload = _normalize_product(_doc)
                                            await _meta_push_one(_sync_client, cfg['meta']['access_token'], cfg['meta']['catalog_id'], _payload)
                                    print(f"[oauth_callback] auto-synced {len(products)} products")
                            except Exception as _e:
                                print(f"[oauth_callback] auto-sync warning: {_e}")

                        return JSONResponse(content={"success": True, "data": {
                            "connected": True,
                            "discovered": assets,
                            "auto_selected": {
                                "instagram_business_account_id": auto_ig_id,
                                "instagram_username":            auto_ig_username,
                                "fb_page_id":                    auto_page_id,
                                "catalog_id":                    auto_catalog,
                            },
                            "needs_selection": (
                                len(assets["instagram_accounts"]) > 1 or
                                len(assets["catalog_list"]) > 1
                            ),
                            "note": "If multiple assets found, call save_meta_config to set specific IDs.",
                        }}, status_code=200)

                    case 'meta_connection_status':
                        row = await _get_row(db, body)
                        if not row:
                            raise Exception("record not found")
                        d    = row.data or {}
                        cfg  = d.get('config', {})
                        meta = cfg.get('meta', {})
                        token      = meta.get('access_token', '')
                        catalog_id = meta.get('catalog_id', '')
                        ig_id      = meta.get('instagram_business_account_id', '')
                        connected  = bool(token)
                        if not connected:
                            return JSONResponse(content={"success": True, "data": {"connected": False}}, status_code=200)

                        # auto-refresh if expiring soon
                        app_id     = cfg.get('meta_app_id', '')
                        app_secret = cfg.get('meta_app_secret', '')
                        refreshed  = await _refresh_token_if_needed(token, app_id, app_secret)
                        if refreshed != token:
                            cfg['meta']  = {**meta, 'access_token': refreshed}
                            d['config']  = cfg
                            row.data     = d
                            await db.commit()
                            token = refreshed

                        catalog_name = ig_username = ''
                        catalog_product_count = 0
                        try:
                            async with httpx.AsyncClient() as client:
                                if catalog_id:
                                    rc = await client.get(
                                        f"https://graph.facebook.com/v19.0/{catalog_id}",
                                        params={"access_token": token, "fields": "id,name,product_count"}
                                    )
                                    rcd                   = rc.json()
                                    catalog_name          = rcd.get('name', '')
                                    catalog_product_count = rcd.get('product_count', 0)
                                if ig_id:
                                    ri = await client.get(
                                        f"https://graph.facebook.com/v19.0/{ig_id}",
                                        params={"access_token": token, "fields": "username,name"}
                                    )
                                    ig_username = ri.json().get('username', meta.get('instagram_username', ''))
                        except Exception:
                            pass

                        # token expiry info
                        token_expires_at = token_days_left = None
                        try:
                            async with httpx.AsyncClient() as _tc:
                                _r  = await _tc.get(
                                    "https://graph.facebook.com/v19.0/debug_token",
                                    params={"input_token": token, "access_token": f"{app_id}|{app_secret}" if app_id and app_secret else token},
                                    timeout=8
                                )
                                _td  = _r.json().get("data", {})
                                _exp = _td.get("expires_at", 0)
                                if _exp and _exp > 0:
                                    token_expires_at = datetime.fromtimestamp(_exp, tz=timezone.utc).isoformat()
                                    token_days_left  = round((_exp - datetime.now(timezone.utc).timestamp()) / 86400)
                        except Exception:
                            pass

                        return JSONResponse(content={"success": True, "data": {
                            "connected":                     True,
                            "instagram_business_account_id": ig_id,
                            "instagram_username":            ig_username,
                            "fb_page_id":                    meta.get('fb_page_id', ''),
                            "fb_page_name":                  meta.get('fb_page_name', ''),
                            "catalog_name":                  catalog_name,
                            "catalog_id":                    catalog_id,
                            "catalog_product_count":         catalog_product_count,
                            "connected_at":                  cfg.get('oauth_connected_at'),
                            "access_token_set":              True,
                            "token_expires_at":              token_expires_at,
                            "token_days_left":               token_days_left,
                        }}, status_code=200)

                    case 'meta_disconnect':
                        row = await _get_row(db, body)
                        if not row:
                            raise Exception("record not found")
                        d   = dict(row.data or {})
                        cfg = dict(d.get('config', {}))
                        existing_meta = cfg.get('meta', {})
                        # clear token only — preserve discovered IDs so reconnect is painless
                        cfg['meta'] = {**existing_meta, 'access_token': ''}
                        cfg.pop('oauth_connected_at', None)
                        d['config'] = cfg
                        row.data    = d
                        await db.commit()
                        return JSONResponse(content={"success": True, "message": "Instagram connection removed."}, status_code=200)

                    # ── instagram_connect — token-based asset discovery + save ─────────

                    case 'instagram_connect':
                        row = await _get_row(db, body)
                        if not row:
                            raise Exception("record not found — create first")
                        token = body.get('access_token') or body.get('meta', {}).get('access_token')
                        if not token:
                            raise Exception("access_token is required")
                        try:
                            assets = await _instagram_discover_assets(token)
                        except Exception as e:
                            return JSONResponse(content={"success": False,
                                "message": f"Instagram asset discovery failed: {e}", "data": {}}, status_code=200)

                        auto_ig_id       = assets["instagram_accounts"][0]["id"]       if len(assets["instagram_accounts"]) == 1 else None
                        auto_ig_username = assets["instagram_accounts"][0]["username"] if len(assets["instagram_accounts"]) == 1 else None
                        auto_page_id     = assets["facebook_pages"][0]["id"]           if len(assets["facebook_pages"]) == 1   else None
                        auto_page_name   = assets["facebook_pages"][0]["name"]         if len(assets["facebook_pages"]) == 1   else None
                        auto_catalog     = assets["catalog_list"][0]["id"]             if len(assets["catalog_list"]) == 1     else None

                        d   = dict(row.data or {})
                        cfg = dict(d.get('config', {}))
                        existing_meta = cfg.get('meta', {})
                        cfg['meta'] = {
                            **existing_meta,
                            'access_token':                  token,
                            'instagram_business_account_id': auto_ig_id       or existing_meta.get('instagram_business_account_id', ''),
                            'instagram_username':            auto_ig_username  or existing_meta.get('instagram_username', ''),
                            'fb_page_id':                    auto_page_id     or existing_meta.get('fb_page_id', ''),
                            'fb_page_name':                  auto_page_name   or existing_meta.get('fb_page_name', ''),
                            'catalog_id':                    auto_catalog     or existing_meta.get('catalog_id', ''),
                        }
                        cfg['oauth_connected_at'] = datetime.now(timezone.utc).isoformat()
                        d['config'] = cfg
                        row.data    = d
                        await db.commit()

                        return JSONResponse(content={"success": True, "data": {
                            "discovered": assets,
                            "auto_selected": {
                                "instagram_business_account_id": auto_ig_id,
                                "instagram_username":            auto_ig_username,
                                "fb_page_id":                    auto_page_id,
                                "catalog_id":                    auto_catalog,
                            },
                            "note": "If multiple assets found, call save_meta_config to set specific IDs.",
                        }}, status_code=200)

                    # ── instagram_validate — health check all connected assets ─────────

                    case 'instagram_validate':
                        row = await _get_row(db, body)
                        if not row:
                            raise Exception("record not found")
                        meta       = _meta_cfg(row)
                        token      = meta.get('access_token')
                        ig_id      = meta.get('instagram_business_account_id')
                        page_id    = meta.get('fb_page_id')
                        catalog_id = meta.get('catalog_id')

                        token_ok = ig_ok = page_ok = catalog_ok = False
                        permissions_detail = {}

                        async with httpx.AsyncClient() as client:
                            # token validity
                            r = await client.get("https://graph.facebook.com/v19.0/me",
                                                 params={"access_token": token})
                            token_ok = "id" in r.json()

                            # Instagram Business Account
                            if ig_id:
                                try:
                                    r2 = await client.get(
                                        f"https://graph.facebook.com/v19.0/{ig_id}",
                                        params={"access_token": token, "fields": "id,username,name"}
                                    )
                                    ig_ok = "id" in r2.json()
                                except Exception:
                                    ig_ok = False
                            else:
                                ig_ok = False  # not configured

                            # Facebook Page
                            if page_id:
                                try:
                                    r3 = await client.get(
                                        f"https://graph.facebook.com/v19.0/{page_id}",
                                        params={"access_token": token, "fields": "id,name"}
                                    )
                                    page_ok = "id" in r3.json()
                                except Exception:
                                    page_ok = False
                            else:
                                page_ok = False  # not configured

                            # Catalog
                            if catalog_id:
                                try:
                                    r4 = await client.get(
                                        f"https://graph.facebook.com/v19.0/{catalog_id}",
                                        params={"access_token": token, "fields": "id,name,product_count"}
                                    )
                                    catalog_ok = "id" in r4.json()
                                except Exception:
                                    catalog_ok = False
                            else:
                                catalog_ok = False  # not configured

                            # permissions check
                            try:
                                rp = await client.get(
                                    f"https://graph.facebook.com/v19.0/me/permissions",
                                    params={"access_token": token}
                                )
                                granted = [p['permission'] for p in rp.json().get('data', []) if p.get('status') == 'granted']
                                required = ['instagram_basic', 'instagram_content_publish', 'pages_show_list', 'catalog_management', 'commerce_management', 'business_management']
                                permissions_detail = {
                                    "granted":  granted,
                                    "required": required,
                                    "missing":  [p for p in required if p not in granted],
                                }
                            except Exception:
                                pass

                        all_ok = token_ok and ig_ok and page_ok and catalog_ok
                        return JSONResponse(content={"success": True, "data": {
                            "token_valid":              token_ok,
                            "instagram_account_ok":     ig_ok,
                            "facebook_page_ok":         page_ok,
                            "catalog_accessible":       catalog_ok,
                            "permissions_valid":        all_ok,
                            "valid":                    all_ok,
                            "permissions":              permissions_detail,
                            "instagram_business_account_id": ig_id or '',
                            "fb_page_id":               page_id or '',
                            "catalog_id":               catalog_id or '',
                        }}, status_code=200)

                    # ── instagram_catalog_details ──────────────────────────

                    case 'instagram_catalog_details':
                        row = await _get_row(db, body)
                        if not row:
                            raise Exception("record not found")
                        meta       = _meta_cfg(row)
                        token      = meta.get('access_token')
                        catalog_id = meta.get('catalog_id')
                        ig_id      = meta.get('instagram_business_account_id', '')
                        if not token:
                            raise Exception("access_token required")

                        catalog_name = ig_username = ''
                        catalog_product_count = 0
                        async with httpx.AsyncClient() as client:
                            if catalog_id:
                                r = await client.get(
                                    f"https://graph.facebook.com/v19.0/{catalog_id}",
                                    params={"access_token": token, "fields": "id,name,product_count"}
                                )
                                rd = r.json()
                                if "error" not in rd:
                                    catalog_name          = rd.get('name', '')
                                    catalog_product_count = rd.get('product_count', 0)
                            if ig_id:
                                ri = await client.get(
                                    f"https://graph.facebook.com/v19.0/{ig_id}",
                                    params={"access_token": token, "fields": "username"}
                                )
                                ig_username = ri.json().get('username', meta.get('instagram_username', ''))

                        run = (await db.execute(
                            select(CatalogSyncHistory)
                            .where(CatalogSyncHistory.business_id == str(row.id))
                            .order_by(CatalogSyncHistory.started_at.desc())
                            .limit(1)
                        )).scalar_one_or_none()

                        return JSONResponse(content={"success": True, "data": {
                            "catalog_id":           catalog_id or '',
                            "catalog_name":         catalog_name,
                            "product_count":        catalog_product_count,
                            "instagram_username":   ig_username,
                            "fb_page_id":           meta.get('fb_page_id', ''),
                            "last_sync":            run.completed_at.isoformat() if run and run.completed_at else None,
                            "meta_connected":       bool(token),
                            "catalog_connected":    bool(catalog_id),
                        }}, status_code=200)

                    # ── instagram_catalog_sync_full ────────────────────────

                    case 'instagram_catalog_sync_full':
                        row = await _get_row(db, body)
                        if not row:
                            raise Exception("record not found")
                        meta       = _meta_cfg(row)
                        token      = meta.get('access_token')
                        catalog_id = meta.get('catalog_id')
                        if not token or not catalog_id:
                            raise Exception("access_token and catalog_id are required")

                        d               = row.data or {}
                        cfg             = d.get('config', {})
                        pd_token        = cfg.get('product_dir_token', '')
                        base_url        = cfg.get('base_url', 'https://fastapi.dryutil.1mn.io')
                        trigger         = body.get('trigger', 'manual')
                        business_id_str = str(row.id)

                        try:
                            pd_resp  = await _fetch_products(pd_token, base_url, per_page=250)
                            products = pd_resp.get('data', {}).get('products',
                                       pd_resp.get('data', {}).get('hits', []))
                            if isinstance(products, dict):
                                products = products.get('hits', products.get('products', []))
                        except Exception as e:
                            raise Exception(f"Failed to fetch products from OMS: {e}")

                        success_count = fail_count = 0
                        sync_id       = uuid.uuid4()
                        started_at    = datetime.now(timezone.utc)
                        completed_at  = started_at
                        final_status  = "failed"

                        async with AsyncSession(_engine) as sync_db:
                            sync_run = CatalogSyncHistory(
                                id=sync_id,
                                business_id=business_id_str,
                                catalog_id=catalog_id,
                                status="running",
                                trigger=trigger,
                                total=len(products),
                            )
                            sync_db.add(sync_run)
                            await sync_db.flush()

                            async with httpx.AsyncClient() as client:
                                for p in products:
                                    doc     = p.get('document', p)
                                    payload = _normalize_product(doc)
                                    pid     = payload["retailer_id"]
                                    pname   = payload["name"]
                                    try:
                                        sc, resp_json = await _meta_push_one(client, token, catalog_id, payload)
                                        ok = sc in (200, 201)
                                        sync_db.add(CatalogSyncLog(
                                            sync_id=sync_id,
                                            business_id=business_id_str,
                                            product_id=pid,
                                            product_name=pname,
                                            status="synced" if ok else "failed",
                                            error=None if ok else str(resp_json),
                                            meta_response=resp_json,
                                        ))
                                        if ok:
                                            success_count += 1
                                        else:
                                            fail_count += 1
                                    except Exception as e:
                                        fail_count += 1
                                        sync_db.add(CatalogSyncLog(
                                            sync_id=sync_id,
                                            business_id=business_id_str,
                                            product_id=pid,
                                            product_name=pname,
                                            status="failed",
                                            error=str(e),
                                        ))

                            completed_at = datetime.now(timezone.utc)
                            final_status = "completed" if fail_count == 0 else ("partial" if success_count > 0 else "failed")
                            sync_run.synced       = success_count
                            sync_run.failed       = fail_count
                            sync_run.status       = final_status
                            sync_run.completed_at = completed_at
                            await sync_db.commit()

                        # update catalog snapshot on business row
                        from sqlalchemy import text as sa_text
                        import json as _json
                        catalog_snap = _json.dumps({
                            "last_sync":      completed_at.isoformat(),
                            "total_products": len(products),
                            "synced":         success_count,
                            "failed":         fail_count,
                            "sync_health":    final_status,
                        })
                        await db.execute(sa_text(
                            f"UPDATE instagram_business SET data = jsonb_set(data, '{{catalog}}', '{catalog_snap}'::jsonb) WHERE id = '{business_id_str}'::uuid"
                        ))
                        await db.commit()

                        # link catalog to Instagram Shop after sync
                        _ig_id = meta.get('instagram_business_account_id', '')
                        if _ig_id and catalog_id:
                            try:
                                await _link_catalog_to_instagram_shop(token, _ig_id, catalog_id)
                            except Exception as e:
                                print(f"[instagram_catalog_sync_full] catalog link warning: {e}")

                        return JSONResponse(content={"success": True, "data": {
                            "sync_id":      str(sync_id),
                            "status":       final_status,
                            "total":        len(products),
                            "synced":       success_count,
                            "failed":       fail_count,
                            "started_at":   started_at.isoformat(),
                            "completed_at": completed_at.isoformat(),
                        }}, status_code=200)

                    # ── instagram_catalog_sync_product — single product sync ───────────

                    case 'instagram_catalog_sync_product':
                        row = await _get_row(db, body)
                        if not row:
                            raise Exception("record not found")
                        meta       = _meta_cfg(row)
                        token      = meta.get('access_token')
                        catalog_id = meta.get('catalog_id')
                        if not token or not catalog_id:
                            raise Exception("access_token and catalog_id are required")
                        product = body.get('product')
                        if not product:
                            raise Exception("product object is required")
                        payload = _normalize_product(product)
                        async with httpx.AsyncClient() as client:
                            sc, resp_json = await _meta_push_one(client, token, catalog_id, payload)
                        ok = sc in (200, 201)
                        return JSONResponse(content={"success": ok, "data": {
                            "retailer_id":   payload["retailer_id"],
                            "meta_response": resp_json,
                            "status":        "synced" if ok else "failed",
                        }}, status_code=200)

                    # ── instagram_catalog_status ───────────────────────────

                    case 'instagram_catalog_status':
                        row = await _get_row(db, body)
                        if not row:
                            raise Exception("record not found")
                        meta       = _meta_cfg(row)
                        token      = meta.get('access_token', '')
                        catalog_id = meta.get('catalog_id', '')
                        connected  = bool(token and catalog_id)
                        product_count = 0
                        catalog_name  = ''
                        if connected:
                            try:
                                async with httpx.AsyncClient() as client:
                                    r = await client.get(
                                        f"https://graph.facebook.com/v19.0/{catalog_id}",
                                        params={"access_token": token, "fields": "id,name,product_count"}
                                    )
                                    rj            = r.json()
                                    product_count = rj.get('product_count', 0)
                                    catalog_name  = rj.get('name', '')
                            except Exception:
                                pass

                        run = (await db.execute(
                            select(CatalogSyncHistory)
                            .where(CatalogSyncHistory.business_id == str(row.id))
                            .order_by(CatalogSyncHistory.started_at.desc())
                            .limit(1)
                        )).scalar_one_or_none()

                        health = "unknown"
                        if run:
                            health = "good" if run.failed == 0 else ("partial" if run.synced > 0 else "failed")

                        return JSONResponse(content={"success": True, "data": {
                            "connected":    connected,
                            "catalog_id":   catalog_id,
                            "catalog_name": catalog_name,
                            "product_count": product_count,
                            "sync_health":  health,
                            "last_sync":    run.completed_at.isoformat() if run and run.completed_at else None,
                        }}, status_code=200)

                    # ── instagram_sync_history — paginated sync runs ───────

                    case 'instagram_sync_history':
                        row = await _get_row(db, body)
                        if not row:
                            raise Exception("record not found")
                        limit  = int(body.get('limit', 20))
                        offset = int(body.get('offset', 0))
                        runs = (await db.execute(
                            select(CatalogSyncHistory)
                            .where(CatalogSyncHistory.business_id == str(row.id))
                            .order_by(CatalogSyncHistory.started_at.desc())
                            .limit(limit).offset(offset)
                        )).scalars().all()
                        return JSONResponse(content={"success": True, "data": {
                            "history": [{
                                "id":             str(r.id),
                                "catalog_id":     r.catalog_id,
                                "status":         r.status,
                                "total_products": r.total,
                                "synced":         r.synced,
                                "failed":         r.failed,
                                "trigger":        r.trigger,
                                "started_at":     r.started_at.isoformat() if r.started_at else None,
                                "completed_at":   r.completed_at.isoformat() if r.completed_at else None,
                            } for r in runs],
                        }}, status_code=200)

                    # ── instagram_sync_errors — failed products ────────────

                    case 'instagram_sync_errors':
                        row = await _get_row(db, body)
                        if not row:
                            raise Exception("record not found")
                        sync_id = body.get('sync_id')
                        if not sync_id:
                            run = (await db.execute(
                                select(CatalogSyncHistory)
                                .where(CatalogSyncHistory.business_id == str(row.id))
                                .order_by(CatalogSyncHistory.started_at.desc())
                                .limit(1)
                            )).scalar_one_or_none()
                            if not run:
                                return JSONResponse(content={"success": True,
                                    "data": {"errors": [], "total_errors": 0}}, status_code=200)
                            sync_id = str(run.id)
                        logs = (await db.execute(
                            select(CatalogSyncLog)
                            .where(
                                CatalogSyncLog.sync_id == uuid.UUID(sync_id),
                                CatalogSyncLog.status == "failed"
                            )
                            .order_by(CatalogSyncLog.created_at.asc())
                        )).scalars().all()
                        return JSONResponse(content={"success": True, "data": {
                            "sync_id":      sync_id,
                            "total_errors": len(logs),
                            "errors": [{
                                "id":         str(l.id),
                                "product_id": l.product_id,
                                "name":       l.product_name,
                                "reason":     l.error,
                            } for l in logs],
                        }}, status_code=200)

                    # ── instagram_health — full platform health check ───────

                    case 'instagram_health':
                        row = await _get_row(db, body)
                        if not row:
                            raise Exception("record not found")
                        meta       = _meta_cfg(row)
                        token      = meta.get('access_token')
                        ig_id      = meta.get('instagram_business_account_id')
                        page_id    = meta.get('fb_page_id')
                        catalog_id = meta.get('catalog_id')

                        checks = {
                            "token":             False,
                            "instagram_account": False,
                            "facebook_page":     False,
                            "catalog":           False,
                        }
                        details = {}

                        if token:
                            async with httpx.AsyncClient() as client:
                                try:
                                    r = await client.get("https://graph.facebook.com/v19.0/me",
                                                         params={"access_token": token}, timeout=8)
                                    checks["token"] = "id" in r.json()
                                    details["token"] = r.json()
                                except Exception as e:
                                    details["token_error"] = str(e)

                                if ig_id:
                                    try:
                                        r2 = await client.get(
                                            f"https://graph.facebook.com/v19.0/{ig_id}",
                                            params={"access_token": token, "fields": "id,username,name"}, timeout=8
                                        )
                                        checks["instagram_account"] = "id" in r2.json()
                                        details["instagram_account"] = r2.json()
                                    except Exception as e:
                                        details["instagram_account_error"] = str(e)

                                if page_id:
                                    try:
                                        r3 = await client.get(
                                            f"https://graph.facebook.com/v19.0/{page_id}",
                                            params={"access_token": token, "fields": "id,name"}, timeout=8
                                        )
                                        checks["facebook_page"] = "id" in r3.json()
                                        details["facebook_page"] = r3.json()
                                    except Exception as e:
                                        details["facebook_page_error"] = str(e)

                                if catalog_id:
                                    try:
                                        r4 = await client.get(
                                            f"https://graph.facebook.com/v19.0/{catalog_id}",
                                            params={"access_token": token, "fields": "id,name,product_count"}, timeout=8
                                        )
                                        checks["catalog"] = "id" in r4.json()
                                        details["catalog"] = r4.json()
                                    except Exception as e:
                                        details["catalog_error"] = str(e)

                        overall = all(checks.values())
                        return JSONResponse(content={"success": True, "data": {
                            "healthy": overall,
                            "checks":  checks,
                            "details": details,
                            "instagram_business_account_id": ig_id or '',
                            "fb_page_id":                    page_id or '',
                            "catalog_id":                    catalog_id or '',
                        }}, status_code=200)

                    # ── catalog_delete_product (shared) ────────────────────

                    case 'catalog_delete_product':
                        row = await _get_row(db, body)
                        if not row:
                            raise Exception("record not found")
                        meta        = _meta_cfg(row)
                        token       = meta.get('access_token')
                        catalog_id  = meta.get('catalog_id')
                        if not token or not catalog_id:
                            raise Exception("access_token and catalog_id are required")
                        retailer_id = body.get('retailer_id') or body.get('product_id')
                        if not retailer_id:
                            raise Exception("retailer_id is required")
                        async with httpx.AsyncClient() as client:
                            sc, resp_json = await _meta_delete_one(client, token, catalog_id, retailer_id)
                        return JSONResponse(content={"success": sc in (200, 201, 204), "data": {
                            "retailer_id":   retailer_id,
                            "meta_response": resp_json,
                        }}, status_code=200)

                    # ── Profile CRUD ───────────────────────────────────────

                    case 'get_profile':
                        row = await _get_row(db, body)
                        if not row:
                            row = await _get_first_business_row(db)
                        if not row:
                            raise Exception("no business record found")
                        d = row.data or {}
                        return JSONResponse(content={"success": True, "data": {
                            "id":          str(row.id),
                            "profile":     d.get('profile', {}),
                            "title":       d.get('profile', {}).get('title', d.get('title', '')),
                            "description": d.get('profile', {}).get('description', ''),
                            "category":    d.get('profile', {}).get('category', ''),
                            "logo_url":    d.get('profile', {}).get('logo_url', ''),
                        }}, status_code=200)

                    case 'save_profile':
                        row = await _get_row(db, body)
                        if not row:
                            raise Exception("record not found")
                        profile_data = body.get('profile', body.get('data', {}))
                        _row_id = str(row.id)
                        import json as _json
                        from sqlalchemy import text as sa_text
                        _profile_json = _json.dumps(profile_data).replace("'", "''")
                        await db.execute(sa_text(
                            f"UPDATE instagram_business SET data = jsonb_set(data, '{{profile}}', '{_profile_json}'::jsonb) WHERE id = '{_row_id}'::uuid"
                        ))
                        await db.commit()
                        return JSONResponse(content={"success": True, "data": {}}, status_code=200)

                    case 'token_refresh':
                        refresh_token = body.get('refresh_token', '')
                        if not refresh_token:
                            raise Exception("refresh_token is required")
                        try:
                            payload = JWTHandler.verify_token(refresh_token)
                        except Exception:
                            raise Exception("invalid or expired refresh token")
                        if payload.get('token_type') != 'refresh':
                            raise Exception("not a refresh token")
                        user_id  = payload.get('sub', '')
                        new_token = _create_access_token(user_id, payload.get('name', ''))
                        return JSONResponse(content={"success": True, "data": {
                            "access_token": new_token,
                            "token_type":   "Bearer"
                        }}, status_code=200)

                    case _:
                        raise Exception(f"unknown typ={typ}")
        
        except Exception as e:
            _log.error(f"[705/i] typ={request.query_params.get('typ')} error={e}")
            return _err("Err [i]", str(e))


    # ── i_init ────────────────────────────────────────────────────────────

    async def i_init(request: Request):
        return


    # ── get_schema_for_create ─────────────────────────────────────────────

    async def get_schema_for_create(request: Request):
        return {
            'body': {
                "type": "object", "required": ["data"],
                "properties": {
                    "data": {
                        "type": "object", "required": ["config"],
                        "properties": {
                            "config": {
                                "type": "object", "required": ["database"],
                                "properties": {
                                    "database": {
                                        "type": "object", "required": ["url"],
                                        "properties": {"url": {"type": "string"}}
                                    },
                                    "meta": {
                                        "type": "object",
                                        "properties": {
                                            "access_token":                  {"type": "string"},
                                            "instagram_business_account_id": {"type": "string"},
                                            "instagram_username":            {"type": "string"},
                                            "fb_page_id":                    {"type": "string"},
                                            "fb_page_name":                  {"type": "string"},
                                            "catalog_id":                    {"type": "string"},
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                "example": {"data": {"config": {
                    "database": {"url": "postgresql+asyncpg://user:pass@localhost:5432/db"},
                    "meta": {
                        "access_token":                  "",
                        "instagram_business_account_id": "",
                        "instagram_username":            "",
                        "fb_page_id":                    "",
                        "fb_page_name":                  "",
                        "catalog_id":                    "",
                    }
                }}}
            },
            'querystring': {}
        }


    # ── get_schema_for_run ────────────────────────────────────────────────

    async def get_schema_for_run(request: Request):
        typ = dict(request.query_params).get('typ')

        def _obj(**props):
            return {"type": "object", "additionalProperties": True, "properties": props}

        _schemas = {
            # CRUD
            'create':  _obj(user_id={"type": "string"}, data={"type": "object"}),
            'get':     _obj(id={"type": "string"}),
            'list':    _obj(user_id={"type": "string"}),
            'update':  _obj(user_id={"type": "string"}, data={"type": "object"}),
            'delete':  _obj(id={"type": "string"}),
            # config
            'meta_config_save':    _obj(id={"type": "string"}, user_id={"type": "string"}, meta={"type": "object"}),
            'save_meta_config':    _obj(id={"type": "string"}, user_id={"type": "string"}, meta={"type": "object"}),
            'get_meta_config':     _obj(id={"type": "string"}, user_id={"type": "string"}),
            # oauth
            'meta_oauth_start':    _obj(id={"type": "string"}, user_id={"type": "string"}, redirect_uri={"type": "string"}, state={"type": "string"}),
            'meta_oauth_callback': _obj(id={"type": "string"}, user_id={"type": "string"}, code={"type": "string"}, redirect_uri={"type": "string"}),
            'meta_connection_status': _obj(id={"type": "string"}, user_id={"type": "string"}),
            'meta_disconnect':     _obj(id={"type": "string"}, user_id={"type": "string"}),
            # instagram
            'instagram_connect':              _obj(id={"type": "string"}, user_id={"type": "string"}, access_token={"type": "string"}),
            'instagram_validate':             _obj(id={"type": "string"}, user_id={"type": "string"}),
            'instagram_catalog_details':      _obj(id={"type": "string"}, user_id={"type": "string"}),
            'instagram_catalog_sync_full':    _obj(id={"type": "string"}, user_id={"type": "string"}, trigger={"type": "string"}),
            'instagram_catalog_sync_product': _obj(id={"type": "string"}, user_id={"type": "string"}, product={"type": "object"}),
            'instagram_catalog_status':       _obj(id={"type": "string"}, user_id={"type": "string"}),
            'instagram_sync_history':         _obj(id={"type": "string"}, user_id={"type": "string"}, limit={"type": "integer"}, offset={"type": "integer"}),
            'instagram_sync_errors':          _obj(id={"type": "string"}, user_id={"type": "string"}, sync_id={"type": "string"}),
            'instagram_health':               _obj(id={"type": "string"}, user_id={"type": "string"}),
            # catalog shared
            'catalog_delete_product': _obj(id={"type": "string"}, user_id={"type": "string"}, retailer_id={"type": "string"}),
            # profile
            'get_profile':  _obj(id={"type": "string"}, user_id={"type": "string"}),
            'save_profile': _obj(id={"type": "string"}, user_id={"type": "string"}, profile={"type": "object"}),
            # token
            'token_refresh': _obj(refresh_token={"type": "string"}),
        }

        if typ not in _schemas:
            raise Exception(f"no body schema found for [typ={typ}]")

        return {
            "body": _schemas[typ],
            "querystring": {
                "type": "object", "required": ["typ"],
                "properties": {"typ": {"type": "string", "enum": list(_schemas.keys())}}
            }
        }


    # ── get_doc_for_run ───────────────────────────────────────────────────

    async def get_doc_for_run(request: Request):
        _var  = {"ep_name": f"client/api/i/{_p['data']['instance'].project.name}/{_p['data']['instance'].utility.name}"}
        _typs = list((await get_schema_for_run(fake_req_obj(
            method="POST", url="", headers={}, query_params={"typ": "create"},
            path_params={}, json_data={}, state={}
        )))['querystring']['properties']['typ']['enum'])

        paths, schemas = {}, {}
        for typ in _typs:
            paths[f"/{_var['ep_name']}?typ={typ}"] = {
                "post": {
                    "summary": typ,
                    "requestBody": {"required": True, "content": {"application/json": {"schema": {"$ref": f"#/components/schemas/{typ}"}}}},
                    "responses": {"200": {"description": "Successful Response"}},
                }
            }
            schemas[typ] = (await get_schema_for_run(fake_req_obj(
                method="POST", url="", headers={}, query_params={"typ": typ},
                path_params={}, json_data={}, state={}
            )))['body']

        return {
            "openapi": "3.0.3",
            "info": {
                "title": "[Instagram Business Commerce] api-docs",
                "description": f"Project={_p['data']['instance'].project.name}, Instance={_p['data']['instance'].name}, Utility-id={_p['data']['instance'].utility.id}",
                "version": "1.0.0",
            },
            "paths": paths,
            "components": {"schemas": schemas},
        }


    return i, get_schema_for_create, get_schema_for_run, i_init, get_doc_for_run
