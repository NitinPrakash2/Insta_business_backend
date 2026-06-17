# 🔗 Seller Instagram Login - Complete Error-Free Setup

## Phase 1: Meta Developer Setup (One-Time Only)

### Step 1.1: Create Meta App
1. Go to https://developers.facebook.com/apps
2. Click **Create App**
3. Select **Business** as app type
4. Fill in:
   - **App Name:** `Instagram Commerce` (any name)
   - **App Purpose:** Select your category
5. Click **Create App**

### Step 1.2: Copy Credentials
- Copy **App ID** from Dashboard
- Go to **Settings → Basic** and copy **App Secret**
- Store these safely (next step)

### Step 1.3: Set Redirect URI
1. Go to **Products → Instagram → Basic Display**
2. Under **Instagram Basic Display → Settings**
3. Add **Valid OAuth Redirect URIs:**
   ```
   http://localhost:5173/oauth/callback          (development)
   https://yourdomain.com/oauth/callback         (production)
   ```
4. Save Changes

### Step 1.4: Add Instagram Permissions
1. Go to **Products → Instagram → Permissions**
2. Request these permissions:
   - `instagram_basic` ✅
   - `instagram_content_publish` ✅
   - `instagram_manage_insights` ✅
   - `pages_show_list` ✅
   - `pages_read_engagement` ✅
   - `catalog_management` ✅
   - `business_management` ✅

> ⚠️ Wait for Meta approval (usually 1-2 days for production)

---

## Phase 2: Backend Instance Configuration

### Step 2.1: Update Database Config

Connect to PostgreSQL (pgAdmin or CLI) and run:

```sql
UPDATE instance 
SET data = jsonb_set(
    jsonb_set(
        jsonb_set(
            jsonb_set(
                COALESCE(data, '{}'),
                '{config,meta_app_id}',
                '"YOUR_APP_ID_HERE"'
            ),
            '{config,meta_app_secret}',
            '"YOUR_APP_SECRET_HERE"'
        ),
        '{config,oauth_redirect_uri}',
        '"http://localhost:5173/oauth/callback"'
    ),
    '{config,product_dir_token}',
    '"YOUR_PRODUCT_DIR_TOKEN"'
)
WHERE name = 'default';
```

Replace:
- `YOUR_APP_ID_HERE` → from Step 1.2
- `YOUR_APP_SECRET_HERE` → from Step 1.2
- `YOUR_PRODUCT_DIR_TOKEN` → your product directory API token

### Step 2.2: Verify Config
```sql
SELECT data->'config' FROM instance WHERE name = 'default';
```

Should show:
```json
{
  "meta_app_id": "123456789",
  "meta_app_secret": "abc123def456",
  "oauth_redirect_uri": "http://localhost:5173/oauth/callback",
  "product_dir_token": "token_xyz"
}
```

---

## Phase 3: Frontend Integration

### Step 3.1: Add Route
In your Vue router, add the Instagram Connect page:

```javascript
{
  path: '/instagram-connect',
  component: () => import('@/hydrator/src/views/InstagramConnect.vue'),
  meta: { requiresAuth: true }
}
```

### Step 3.2: OAuth Callback Ready
The static HTML file at `/public/oauth/callback/index.html` automatically:
- Captures authorization code from Meta
- Exchanges code for token (via backend)
- Discovers Instagram accounts & catalogs
- Redirects to dashboard

No extra setup needed! ✅

---

## Phase 4: Seller Flow (User-Friendly)

### For Seller:

#### Step 1: Click "Connect Instagram"
- Redirects to Facebook OAuth dialog
- Seller logs in with Instagram Business account
- Grants permissions

#### Step 2: Auto-Discovery
Backend automatically finds:
- ✅ All Instagram Business Accounts
- ✅ All Facebook Pages
- ✅ All Product Catalogs
- ✅ Auto-creates catalog if none exist

#### Step 3: Select & Sync
If multiple found:
- Choose Instagram account
- Choose product catalog

Then:
- **Save** → Stores selection
- **Sync** → Uploads all products to catalog (error-free)

#### Step 4: Done ✅
- Products visible on Instagram Shop
- Status dashboard shows sync details
- Can re-sync anytime

---

## API Endpoints Reference

All endpoints POST to: `/client/api/i/ona/instagram`

### OAuth Flow
```bash
# Start OAuth
curl -X POST "http://localhost:8000/client/api/i/ona/instagram?typ=meta_oauth_start" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "seller_123",
    "redirect_uri": "http://localhost:5173/oauth/callback"
  }'

# Callback (automatic from OAuth redirect)
# Backend handles: /oauth/callback → exchanges code → saves config

# Check connection status
curl -X POST "http://localhost:8000/client/api/i/ona/instagram?typ=meta_connection_status" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "seller_123"}'
```

### Config Management
```bash
# Get current config
curl -X POST "http://localhost:8000/client/api/i/ona/instagram?typ=get_meta_config" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "seller_123"}'

# Save selected accounts
curl -X POST "http://localhost:8000/client/api/i/ona/instagram?typ=save_meta_config" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "seller_123",
    "meta": {
      "instagram_business_account_id": "ig_123456",
      "catalog_id": "cat_789012"
    }
  }'
```

### Syncing
```bash
# Full product sync
curl -X POST "http://localhost:8000/client/api/i/ona/instagram?typ=instagram_catalog_sync_full" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "seller_123", "trigger": "manual"}'

# Check sync history
curl -X POST "http://localhost:8000/client/api/i/ona/instagram?typ=instagram_sync_history" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "seller_123", "limit": 10, "offset": 0}'

# Get sync errors
curl -X POST "http://localhost:8000/client/api/i/ona/instagram?typ=instagram_sync_errors" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "seller_123"}'
```

---

## Troubleshooting

### ❌ "meta_app_id not configured"
**Solution:** Run Step 2.1 SQL update and verify with Step 2.2

### ❌ "Invalid authorization code"
**Solution:** 
- Check redirect URI matches exactly in Meta App settings
- Clear browser cookies and try again
- Verify OAuth_redirect_uri in database config

### ❌ "Instagram account not found"
**Solution:**
- Verify user has admin access to Facebook Business Manager
- Check account has Instagram Business (not personal) setup
- Request missing permissions in Meta App

### ❌ "Products not syncing"
**Solution:**
- Check `product_dir_token` is valid
- Verify catalog products format matches `_normalize_product()` schema
- Check sync errors via `instagram_sync_errors` endpoint
- Verify catalog product count increases

### ❌ OAuth callback blank page
**Solution:**
- Ensure `/public/oauth/callback/index.html` exists
- Check browser console for errors
- Verify backend endpoint `/client/api/i/ona/instagram?typ=meta_oauth_callback` is accessible

---

## Security Checklist

✅ **Never expose credentials in frontend**
- App Secret stored only in backend database
- Access tokens stored securely in encrypted DB column

✅ **Token auto-refresh**
- Tokens auto-refresh 7 days before expiry
- No manual intervention needed

✅ **CORS safe**
- OAuth redirects to static callback page
- Backend validates all requests
- User_id verified from JWT

✅ **Rate limiting**
- API calls rate-limited per user
- Configurable via `RATE_LIMIT_PER_MINUTE` env var

---

## Performance Tips

- **Batch syncing:** Can handle 250+ products per sync
- **Async operations:** Non-blocking product uploads
- **Database indexes:** Automatically created on first run
- **Token caching:** Long-lived tokens reduce OAuth overhead

---

## Next Steps

1. ✅ Complete Phase 1-2 above
2. ✅ Test OAuth flow in dev: `http://localhost:5173/instagram-connect`
3. ✅ Verify sync creates products in Instagram catalog
4. ✅ Deploy to production with correct redirect URIs
5. ✅ Monitor via sync history & error logs

**You're all set! 🚀**
