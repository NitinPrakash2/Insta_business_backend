from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.shared.util.jwt_handler.index import JWTHandler
import os


app = FastAPI(title="FastAPI", version="0.1")

@app.post("/auth/get_token")
async def get_token(body: dict):
    """Generate JWT token for seller."""
    user_id = body.get('user_id', '')
    if not user_id:
        return {"success": False, "message": "user_id required"}
    
    access_token = JWTHandler.create_token(
        {"sub": user_id, "security": {"party": ["party_2"]}, "token_type": "access"},
        expire_minutes=1440
    )
    refresh_token = JWTHandler.create_token(
        {"sub": user_id, "token_type": "refresh", "security": {"party": ["party_2"]}},
        expire_minutes=30 * 24 * 60
    )
    
    return {
        "success": True,
        "data": {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer"
        }
    }


from src.shared.util.include_file.index import include_file
from src.db_config import engine, Base
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




"""
# Create tables if not using Alembic
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

"""




#====party_1====#  [START]
def _party_1(_v=None):
    if _v is None:
        _v = {"party": "party_1"}
    _dta = {
        "app": {
        "global": app,
        "this_public": FastAPI(title="FastAPI", version="0.1"),
        "this_private": FastAPI(title="FastAPI", version="0.1"),
        },
        "prefix": "/admin",
        "prefix_public": "/admin-public",
    }
    AuthMiddleware_name, AuthMiddleware_module = include_file(f"src/parties/{_v['party']}/middlewares/auth.py", lambda name, module: ())[0]
    AuthMiddleware = AuthMiddleware_module.AuthMiddleware 

    include_file(f"src/parties/{_v['party']}/routes", lambda name, module: (
        module.index({}),
        _dta["app"]["this_public"].include_router(module._ins['router']['public'], prefix=""),
        _dta["app"]["this_private"].include_router(module._ins['router']['private'], prefix=""),
        _dta["app"]["global"].mount(_dta["prefix_public"], _dta["app"]["this_public"]),
        _dta["app"]["global"].mount(_dta["prefix"], _dta["app"]["this_private"]),
        _dta["app"]["this_private"].add_middleware(AuthMiddleware),
    ))

_party_1({"party": "party_1"})
#====party_1====#  [END]




#====party_2====#  [START]
def _party_2(_v=None):
    if _v is None:
        _v = {"party": "party_2"}
    _dta = {
        "app": {
        "global": app,
        "this_public": FastAPI(title="FastAPI", version="0.1"),
        "this_private": FastAPI(title="FastAPI", version="0.1"),
        },
        "prefix": "/client",
        "prefix_public": "/client-public",
    }
    AuthMiddleware_name, AuthMiddleware_module = include_file(f"src/parties/{_v['party']}/middlewares/auth.py", lambda name, module: ())[0]
    AuthMiddleware = AuthMiddleware_module.AuthMiddleware 

    include_file(f"src/parties/{_v['party']}/routes", lambda name, module: (
        module.index({}),
        _dta["app"]["this_public"].include_router(module._ins['router']['public'], prefix=""),
        _dta["app"]["this_private"].include_router(module._ins['router']['private'], prefix=""),
        _dta["app"]["global"].mount(_dta["prefix_public"], _dta["app"]["this_public"]),
        _dta["app"]["global"].mount(_dta["prefix"], _dta["app"]["this_private"]),
        _dta["app"]["this_private"].add_middleware(AuthMiddleware),
    ))

_party_2({"party": "party_2"})
#====party_2====#  [END]
