# Instagram Business Commerce - Complete API Testing Guide

## Prerequisites
- Instagram Business Account: ✅ Ready
- Facebook Page: ✅ "Nitin Test" linked
- Server Running: http://localhost:8000
- Database: PostgreSQL connected

---

## Step 0: Database Setup (ONE TIME ONLY)

### Create instagram_business table:
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

Run this in your PostgreSQL:
```bash
psql -U postgres -d dryutil -c "CREATE TABLE IF NOT EXISTS instagram_business (id SERIAL PRIMARY KEY, user_id VARCHAR NOT NULL, data JSONB NOT NULL DEFAULT '{}', created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);"

psql -U postgres -d dryutil -c "CREATE INDEX idx_instagram_business_user_id ON instagram_business(user_id);"
```

---

## Step 1: Generate JWT Token

First, generate a valid JWT token for authentication:

```bash
cd c:\Users\nitin\Desktop\Instagram\Insta_business_backend\dryutil\backend\python\fastapi\project
poetry run python -c "from src.shared.util.jwt_handler.index import JWTHandler; token = JWTHandler.create_token({'sub': 'seller_nitin_001', 'name': 'Nitin', 'security': {'party': ['party_2']}}, expire_minutes=1440); print(f'Bearer {token}')"
```

**Save this token** - you'll use it in all authenticated requests.

---

## Step 2: Create Seller/Instance

### Request:
```bash
POST http://localhost:8000/client/api/i/ona/x?utility_id=705&action=create
Content-Type: application/json
Authorization: Bearer YOUR_JWT_TOKEN

{
  "name": "Nitin Instagram Shop",
  "description": "Test Instagram Business Account for product catalog sync"
}
```

### cURL Command:
```bash
curl -X POST "http://localhost:8000/client/api/i/ona/x?utility_id=705&action=create" ^
  -H "Content-Type: application/json" ^
  -H "Authorization: Bearer YOUR_JWT_TOKEN" ^
  -d "{\"name\":\"Nitin Instagram Shop\",\"description\":\"Test Instagram Business Account for product catalog sync\"}"
```

### Expected Response:
```json
{
  "success": true,
  "message": "Instance created successfully",
  "data": {
    "instance_id": 1,
    "user_id": "seller_nitin_001",
    "utility_id": 705,
    "name": "x",
    "project": "ona",
    "created_at": "2026-06-14T22:45:00Z"
  }
}
```

**Status Code**: 200 or 201

---

## Step 3: Meta OAuth Start

This generates the Meta OAuth URL for user authorization.

### Request:
```bash
GET http://localhost:8000/client-public/api/i/meta_oauth_start?utility_id=705&user_id=seller_nitin_001&instance_name=x&project_name=ona
```

### cURL Command:
```bash
curl "http://localhost:8000/client-public/api/i/meta_oauth_start?utility_id=705&user_id=seller_nitin_001&instance_name=x&project_name=ona"
```

### Expected Response:
```json
{
  "success": true,
  "oauth_url": "https://www.facebook.com/v21.0/dialog/oauth?client_id=YOUR_META_APP_ID&redirect_uri=http://localhost:8000/client-public/api/i/meta_oauth_callback&state=eyJ1dGlsaXR5X2lkIjo3MDUsInVzZXJfaWQiOiJzZWxsZXJfbml0aW5fMDAxIn0&scope=instagram_basic,instagram_content_publish,instagram_manage_insights,pages_show_list,pages_read_engagement,catalog_management,business_management"
}
```

### Action Required:
1. Copy the `oauth_url` from response
2. **Open it in your browser**
3. Login with your Facebook account (if not already logged in)
4. Approve the requested permissions:
   - Instagram Basic Access
   - Instagram Content Publish
   - Instagram Manage Insights
   - Pages Show List
   - Pages Read Engagement
   - Catalog Management
   - Business Management
5. Meta will redirect you to `meta_oauth_callback` automatically

---

## Step 4: Meta OAuth Callback (Automatic)

This endpoint is called automatically by Meta after authorization.

**You don't need to call this manually** - Meta redirects here with the authorization code.

### What Happens:
1. Exchanges `code` for long-lived access token (60 days)
2. Calls `_instagram_discover_assets()`:
   - Discovers Instagram Business Account ID
   - Finds linked Facebook Page ("Nitin Test")
   - Lists all Meta Catalogs
3. Auto-links catalog to Instagram Shop
4. Saves config to `instagram_business` table

### Expected Redirect:
```
http://localhost:8000/client-public/api/i/meta_oauth_callback?code=AQD...xyz&state=eyJ1dGlsaXR5X2lkIjo3MDUsInVzZXJfaWQiOiJzZWxsZXJfbml0aW5fMDAxIn0
```

### Expected Response (shown in browser):
```json
{
  "success": true,
  "message": "Instagram Business Account connected successfully",
  "data": {
    "instagram_username": "your_instagram_username",
    "instagram_business_account_id": "17841XXXXXXXXXX",
    "fb_page_id": "10928XXXXXXXX",
    "fb_page_name": "Nitin Test",
    "catalog_id": "12345678901234567",
    "catalog_name": "Your Catalog Name",
    "token_expires_in": 5184000
  }
}
```

**Status Code**: 200

---

## Step 5: Validate Instagram Connection

Verify that Instagram Business Account is properly connected.

### Request:
```bash
GET http://localhost:8000/client/api/i/ona/x?utility_id=705&action=instagram_validate
Authorization: Bearer YOUR_JWT_TOKEN
```

### cURL Command:
```bash
curl "http://localhost:8000/client/api/i/ona/x?utility_id=705&action=instagram_validate" ^
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Expected Response:
```json
{
  "success": true,
  "valid": true,
  "data": {
    "instagram_business_account_id": "17841XXXXXXXXXX",
    "instagram_username": "your_instagram_username",
    "fb_page_id": "10928XXXXXXXX",
    "fb_page_name": "Nitin Test",
    "catalog_id": "12345678901234567",
    "token_valid": true,
    "token_expires_at": "2026-08-13T22:45:00Z",
    "shop_linked": true
  }
}
```

**Status Code**: 200

### If Not Connected:
```json
{
  "success": false,
  "valid": false,
  "error": "No Instagram Business configuration found"
}
```

---

## Step 6: Full Catalog Sync

Sync all products from your OMS to Instagram Shop via Meta Catalog.

### Request:
```bash
POST http://localhost:8000/client/api/i/ona/x?utility_id=705&action=instagram_catalog_sync_full
Content-Type: application/json
Authorization: Bearer YOUR_JWT_TOKEN

{}
```

### cURL Command:
```bash
curl -X POST "http://localhost:8000/client/api/i/ona/x?utility_id=705&action=instagram_catalog_sync_full" ^
  -H "Content-Type: application/json" ^
  -H "Authorization: Bearer YOUR_JWT_TOKEN" ^
  -d "{}"
```

### Expected Response:
```json
{
  "success": true,
  "message": "Full catalog sync initiated",
  "data": {
    "sync_id": "sync_1718396700_seller_nitin_001",
    "total_products_fetched": 25,
    "synced": 23,
    "failed": 2,
    "skipped": 0,
    "sync_started_at": "2026-06-14T22:45:00Z",
    "sync_completed_at": "2026-06-14T22:45:15Z",
    "duration_seconds": 15
  }
}
```

**Status Code**: 200

### What Happens:
1. Fetches all products from OMS (your product database)
2. Normalizes each product (price, images, description)
3. Pushes to Meta Catalog via Graph API
4. Links products to Instagram Shop
5. Logs each product sync in `catalog_sync_log` table
6. Creates history entry in `catalog_sync_history` table

---

## Step 7: Check Catalog Details

View current catalog information and product count.

### Request:
```bash
GET http://localhost:8000/client/api/i/ona/x?utility_id=705&action=instagram_catalog_details
Authorization: Bearer YOUR_JWT_TOKEN
```

### cURL Command:
```bash
curl "http://localhost:8000/client/api/i/ona/x?utility_id=705&action=instagram_catalog_details" ^
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Expected Response:
```json
{
  "success": true,
  "data": {
    "catalog_id": "12345678901234567",
    "catalog_name": "Your Catalog Name",
    "business_id": "98765432109876543",
    "product_count": 23,
    "vertical": "commerce",
    "instagram_shop_linked": true,
    "products_sample": [
      {
        "id": "1234567890",
        "name": "Product Name 1",
        "price": "2999.00 INR",
        "availability": "in stock",
        "url": "https://yourstore.com/product-1",
        "image_url": "https://cdn.yourstore.com/image1.jpg"
      },
      {
        "id": "1234567891",
        "name": "Product Name 2",
        "price": "1499.00 INR",
        "availability": "in stock",
        "url": "https://yourstore.com/product-2",
        "image_url": "https://cdn.yourstore.com/image2.jpg"
      }
    ]
  }
}
```

**Status Code**: 200

---

## Step 8: Check Sync History

View all previous sync operations.

### Request:
```bash
GET http://localhost:8000/client/api/i/ona/x?utility_id=705&action=instagram_sync_history
Authorization: Bearer YOUR_JWT_TOKEN
```

### cURL Command:
```bash
curl "http://localhost:8000/client/api/i/ona/x?utility_id=705&action=instagram_sync_history" ^
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Expected Response:
```json
{
  "success": true,
  "data": {
    "total_syncs": 1,
    "history": [
      {
        "id": 1,
        "sync_id": "sync_1718396700_seller_nitin_001",
        "user_id": "seller_nitin_001",
        "sync_type": "full",
        "status": "completed",
        "total_products": 25,
        "success_count": 23,
        "failed_count": 2,
        "started_at": "2026-06-14T22:45:00Z",
        "completed_at": "2026-06-14T22:45:15Z",
        "duration_seconds": 15
      }
    ]
  }
}
```

**Status Code**: 200

---

## Step 9: Check Sync Errors (if any)

View detailed error logs for failed products.

### Request:
```bash
GET http://localhost:8000/client/api/i/ona/x?utility_id=705&action=instagram_sync_errors
Authorization: Bearer YOUR_JWT_TOKEN
```

### cURL Command:
```bash
curl "http://localhost:8000/client/api/i/ona/x?utility_id=705&action=instagram_sync_errors" ^
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Expected Response:
```json
{
  "success": true,
  "data": {
    "total_errors": 2,
    "errors": [
      {
        "id": 1,
        "sync_id": "sync_1718396700_seller_nitin_001",
        "product_id": "prod_123",
        "product_name": "Product With Error",
        "status": "failed",
        "error_message": "Invalid image URL: Image must be accessible",
        "meta_response": "{\"error\": {\"code\": 100, \"message\": \"Invalid parameter\"}}",
        "attempted_at": "2026-06-14T22:45:05Z"
      },
      {
        "id": 2,
        "sync_id": "sync_1718396700_seller_nitin_001",
        "product_id": "prod_456",
        "product_name": "Out of Stock Item",
        "status": "failed",
        "error_message": "Price validation failed: Price must be greater than 0",
        "meta_response": null,
        "attempted_at": "2026-06-14T22:45:08Z"
      }
    ]
  }
}
```

**Status Code**: 200

---

## Step 10: Sync Individual Product

Update or add a single product to the catalog.

### Request:
```bash
POST http://localhost:8000/client/api/i/ona/x?utility_id=705&action=instagram_catalog_sync_product
Content-Type: application/json
Authorization: Bearer YOUR_JWT_TOKEN

{
  "product_id": "prod_789"
}
```

### cURL Command:
```bash
curl -X POST "http://localhost:8000/client/api/i/ona/x?utility_id=705&action=instagram_catalog_sync_product" ^
  -H "Content-Type: application/json" ^
  -H "Authorization: Bearer YOUR_JWT_TOKEN" ^
  -d "{\"product_id\":\"prod_789\"}"
```

### Expected Response:
```json
{
  "success": true,
  "message": "Product synced successfully",
  "data": {
    "product_id": "prod_789",
    "product_name": "Updated Product Name",
    "meta_product_id": "1234567892",
    "status": "synced",
    "synced_at": "2026-06-14T22:50:00Z"
  }
}
```

**Status Code**: 200

---

## Step 11: Check Instagram Health

Overall health check of Instagram integration.

### Request:
```bash
GET http://localhost:8000/client/api/i/ona/x?utility_id=705&action=instagram_health
Authorization: Bearer YOUR_JWT_TOKEN
```

### cURL Command:
```bash
curl "http://localhost:8000/client/api/i/ona/x?utility_id=705&action=instagram_health" ^
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Expected Response:
```json
{
  "success": true,
  "health": "healthy",
  "data": {
    "instagram_connected": true,
    "token_valid": true,
    "token_expires_in_days": 58,
    "catalog_linked": true,
    "shop_active": true,
    "total_products_synced": 23,
    "last_sync": "2026-06-14T22:45:00Z",
    "failed_syncs_last_24h": 0,
    "api_rate_limit_ok": true
  }
}
```

**Status Code**: 200

---

## Troubleshooting

### Issue 1: meta_oauth_start returns 404
**Cause**: Route not registered in public router  
**Solution**: Check if OAuth routes are in public router, not private

### Issue 2: OAuth callback fails with "Invalid state"
**Cause**: State parameter mismatch or expired  
**Solution**: Generate fresh oauth_start URL and complete flow within 10 minutes

### Issue 3: instagram_validate returns "No configuration found"
**Cause**: OAuth flow not completed or database entry missing  
**Solution**: Complete OAuth flow (Step 3-4) again

### Issue 4: Catalog sync fails with "Token expired"
**Cause**: Access token expired (60 days validity)  
**Solution**: Re-run OAuth flow to get new long-lived token

### Issue 5: Products not visible in Instagram Shop
**Cause**: Meta requires manual approval for Instagram Shop visibility  
**Solution**: Wait 1-5 business days for Meta review, check Commerce Manager

### Issue 6: "Catalog not linked to Instagram Shop"
**Cause**: Auto-linking failed during OAuth callback  
**Solution**: Manually link in Facebook Commerce Manager or re-run OAuth flow

---

## Database Queries for Verification

### Check instance created:
```sql
SELECT * FROM instance WHERE user_id = 'seller_nitin_001' AND utility_id = 705;
```

### Check Instagram Business config:
```sql
SELECT * FROM instagram_business WHERE user_id = 'seller_nitin_001';
```

### Check sync history:
```sql
SELECT * FROM catalog_sync_history WHERE user_id = 'seller_nitin_001' ORDER BY created_at DESC;
```

### Check product sync logs:
```sql
SELECT * FROM catalog_sync_log WHERE user_id = 'seller_nitin_001' ORDER BY created_at DESC LIMIT 10;
```

---

## Success Criteria

✅ **Step 1**: Instance created in database  
✅ **Step 2-4**: OAuth completed, token stored, assets discovered  
✅ **Step 5**: Validation shows `valid: true`  
✅ **Step 6**: Products synced to Meta Catalog  
✅ **Step 7**: Catalog details show correct product count  
✅ **Step 8**: Sync history logged  
✅ **Step 11**: Health check shows `healthy`  

🎉 **Integration Complete!**

---

## Next Steps After Testing

1. **Business Verification**: Complete Meta Business Verification for Shop approval
2. **Product Review**: Meta will review products (1-5 days)
3. **Shop Visibility**: Instagram Shop becomes visible after approval
4. **Automated Sync**: Set up cron job for periodic catalog sync
5. **Webhook Integration**: Add webhook for real-time product updates
6. **Monitoring**: Set up alerts for sync failures

---

## Notes

- **Token Validity**: 60 days (long-lived token)
- **Rate Limits**: Meta Graph API has rate limits (200 calls/hour/user)
- **Product Approval**: Meta reviews products for policy compliance
- **Shop Visibility**: Requires Business Verification + Product Approval
- **Testing**: Use test products initially to avoid policy violations
