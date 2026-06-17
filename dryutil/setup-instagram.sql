-- ============================================================================
-- Instagram Commerce Setup Script
-- ============================================================================
-- This script configures Meta App credentials and OAuth redirect URI
-- Run this in your PostgreSQL database once after creating Meta App
-- 
-- Replace these values:
-- - YOUR_APP_ID: From https://developers.facebook.com/apps → Dashboard
-- - YOUR_APP_SECRET: From https://developers.facebook.com/apps → Settings → Basic
-- - YOUR_REDIRECT_URI: Must match Meta App OAuth Redirect URIs
-- - YOUR_PRODUCT_DIR_TOKEN: Your internal product directory API token
-- ============================================================================

-- FOR DEVELOPMENT:
UPDATE instance 
SET data = jsonb_set(
    jsonb_set(
        jsonb_set(
            jsonb_set(
                COALESCE(data, '{}'),
                '{config,meta_app_id}',
                '"YOUR_APP_ID"'
            ),
            '{config,meta_app_secret}',
            '"YOUR_APP_SECRET"'
        ),
        '{config,oauth_redirect_uri}',
        '"http://localhost:5173/oauth/callback"'
    ),
    '{config,product_dir_token}',
    '"YOUR_PRODUCT_DIR_TOKEN"'
)
WHERE name = 'default';

-- FOR PRODUCTION:
-- UPDATE instance 
-- SET data = jsonb_set(
--     jsonb_set(
--         jsonb_set(
--             jsonb_set(
--                 COALESCE(data, '{}'),
--                 '{config,meta_app_id}',
--                 '"YOUR_APP_ID"'
--             ),
--             '{config,meta_app_secret}',
--             '"YOUR_APP_SECRET"'
--         ),
--         '{config,oauth_redirect_uri}',
--         '"https://yourdomain.com/oauth/callback"'
--     ),
--     '{config,product_dir_token}',
--     '"YOUR_PRODUCT_DIR_TOKEN"'
-- )
-- WHERE name = 'default';

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- Check if config was saved
SELECT 
  name,
  data->'config'->>'meta_app_id' as app_id,
  data->'config'->>'oauth_redirect_uri' as redirect_uri,
  data->'config'->>'product_dir_token' as product_token
FROM instance 
WHERE name = 'default';

-- Get full config for debugging
SELECT jsonb_pretty(data->'config') FROM instance WHERE name = 'default';

-- Check Instagram Business records (auto-created per seller)
SELECT 
  id,
  user_id,
  data->'config'->'meta'->>'access_token' as token_set,
  data->'config'->'meta'->>'instagram_business_account_id' as ig_account_id,
  data->'config'->'meta'->>'catalog_id' as catalog_id
FROM instagram_business 
LIMIT 10;

-- Check sync history
SELECT 
  id,
  business_id,
  status,
  total,
  synced,
  failed,
  started_at,
  completed_at
FROM catalog_sync_history 
ORDER BY started_at DESC 
LIMIT 20;

-- Check failed products from last sync
SELECT 
  l.sync_id,
  l.product_id,
  l.product_name,
  l.status,
  l.error
FROM catalog_sync_log l
WHERE l.status = 'failed'
ORDER BY l.created_at DESC
LIMIT 50;

-- ============================================================================
-- RESET (if needed)
-- ============================================================================
-- Clear Instagram connection (keeps seller data)
-- UPDATE instagram_business 
-- SET data = jsonb_set(data, '{config,meta,access_token}', '""')
-- WHERE user_id = 'seller_email';

-- Clear all sync history for a seller
-- DELETE FROM catalog_sync_history WHERE business_id = 'seller_id_uuid';
-- DELETE FROM catalog_sync_log WHERE business_id = 'seller_id_uuid';
