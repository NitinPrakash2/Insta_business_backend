# 🚀 Quick Start - Instagram Business API Testing

## Prerequisites ✅
- ✅ Instagram Business Account ready
- ✅ Facebook Page "Nitin Test" linked
- ✅ Server running on http://localhost:8000
- ✅ PostgreSQL database connected

---

## Step 1: Create Database Table (ONE TIME ONLY)

Open PostgreSQL and run:

```sql
CREATE TABLE IF NOT EXISTS instagram_business (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR NOT NULL,
    data JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_instagram_business_user_id ON instagram_business(user_id);
```

Or use command line:
```bash
psql -U postgres -d dryutil -c "CREATE TABLE IF NOT EXISTS instagram_business (id SERIAL PRIMARY KEY, user_id VARCHAR NOT NULL, data JSONB NOT NULL DEFAULT '{}', created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP); CREATE INDEX idx_instagram_business_user_id ON instagram_business(user_id);"
```

---

## Step 2: Generate JWT Token

```bash
cd c:\Users\nitin\Desktop\Instagram\Insta_business_backend\dryutil\backend\python\fastapi\project
poetry run python generate_token.py
```

**Copy the token** that appears after "Bearer" - you'll use it in all API calls.

---

## Step 3: Test APIs Using Postman (RECOMMENDED)

### Import Collection:
1. Open Postman
2. Click "Import"
3. Select file: `Instagram_Business_API.postman_collection.json`
4. Collection will be imported with all 13 endpoints

### Configure Variables:
1. Click on the collection name
2. Go to "Variables" tab
3. Update `jwt_token` with your generated token
4. Save

### Run Tests in Order:
1. ✅ Create Seller Instance
2. ✅ Meta OAuth Start (copy oauth_url from response, open in browser)
3. ✅ Instagram Validate (after OAuth completes)
4. ✅ Instagram Health
5. ✅ Full Catalog Sync
6. ✅ Catalog Details
7. ✅ Sync History

---

## Step 4: Test APIs Using cURL (ALTERNATIVE)

### 1. Generate Token:
```bash
poetry run python generate_token.py
```

Save the token as: `YOUR_TOKEN_HERE`

### 2. Create Seller:
```bash
curl -X POST "http://localhost:8000/client/api/i/ona/x?utility_id=705&action=create" ^
  -H "Content-Type: application/json" ^
  -H "Authorization: Bearer YOUR_TOKEN_HERE" ^
  -d "{\"name\":\"Nitin Instagram Shop\",\"description\":\"Test shop\"}"
```

### 3. Start OAuth:
```bash
curl "http://localhost:8000/client-public/api/i/meta_oauth_start?utility_id=705&user_id=seller_nitin_001&instance_name=x&project_name=ona"
```

**Open the returned `oauth_url` in your browser** and approve permissions.

### 4. Validate Connection:
```bash
curl "http://localhost:8000/client/api/i/ona/x?utility_id=705&action=instagram_validate" ^
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### 5. Sync Full Catalog:
```bash
curl -X POST "http://localhost:8000/client/api/i/ona/x?utility_id=705&action=instagram_catalog_sync_full" ^
  -H "Content-Type: application/json" ^
  -H "Authorization: Bearer YOUR_TOKEN_HERE" ^
  -d "{}"
```

### 6. Check Catalog Details:
```bash
curl "http://localhost:8000/client/api/i/ona/x?utility_id=705&action=instagram_catalog_details" ^
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

## Expected Flow:

```
1. Create Seller → 200 OK
   ↓
2. OAuth Start → Returns oauth_url
   ↓
3. [Browser] Approve permissions → Auto redirects to callback
   ↓
4. Validate → Returns Instagram account details
   ↓
5. Full Sync → Syncs all products
   ↓
6. Catalog Details → Shows synced products
```

---

## Troubleshooting:

### ❌ 400 Bad Request - "Instance not found"
**Fix**: Run Step 3.1 (Create Seller) first

### ❌ 401 Unauthorized
**Fix**: Generate new token using `poetry run python generate_token.py`

### ❌ 404 Not Found on OAuth
**Fix**: Check if server is running and OAuth routes are registered

### ❌ "No Instagram configuration found"
**Fix**: Complete OAuth flow (open oauth_url in browser)

### ❌ Products not syncing
**Fix**: Check if OMS has products, verify catalog_id in database

---

## Verify in Database:

### Check instance:
```sql
SELECT * FROM instance WHERE utility_id = 705;
```

### Check Instagram config:
```sql
SELECT user_id, data->>'instagram_username' as username, 
       data->'config'->'meta'->>'catalog_id' as catalog_id
FROM instagram_business;
```

### Check sync logs:
```sql
SELECT * FROM catalog_sync_history ORDER BY created_at DESC LIMIT 5;
```

---

## 📚 Full Documentation:

- **Complete Guide**: `INSTAGRAM_API_TESTING_GUIDE.md`
- **Health Report**: `API_HEALTH_REPORT.md`
- **Postman Collection**: `Instagram_Business_API.postman_collection.json`

---

## 🎯 Success Checklist:

- [ ] Database table created
- [ ] JWT token generated
- [ ] Seller instance created (200 OK)
- [ ] OAuth completed (browser redirect successful)
- [ ] Validation shows Instagram username
- [ ] Catalog sync runs successfully
- [ ] Products visible in catalog details

Once all ✅, your Instagram Business Commerce integration is LIVE! 🎉
