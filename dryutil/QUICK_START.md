# ✅ Instagram Commerce - Quick Start Checklist

## Pre-Launch Checklist (Admin)

- [ ] Create Meta App at https://developers.facebook.com/apps
- [ ] Copy App ID and App Secret
- [ ] Add valid OAuth Redirect URIs in Meta App settings
- [ ] Request all required permissions (see setup guide)
- [ ] Wait for Meta approval
- [ ] Run SQL setup script with credentials
- [ ] Verify database config: `SELECT data->'config' FROM instance WHERE name = 'default';`
- [ ] Test backend endpoint is accessible: `curl http://localhost:8000/client/api/i/ona/instagram?typ=meta_oauth_start`
- [ ] Ensure `/public/oauth/callback/index.html` exists on frontend
- [ ] Add InstagramConnect.vue component to router
- [ ] Test frontend route: `http://localhost:5173/instagram-connect`

## Seller Launch Day

### 1️⃣ Setup (5 minutes)
```
Go to: http://localhost:5173/instagram-connect
Click: [Connect Instagram]
```

### 2️⃣ Login (2 minutes)
```
1. Facebook login dialog appears
2. Log in with Instagram Business account
3. Grant permissions
```

### 3️⃣ Auto-Discovery (30 seconds)
```
Backend discovers:
✅ Instagram Accounts
✅ Facebook Pages  
✅ Product Catalogs
✅ Auto-creates catalog if needed
```

### 4️⃣ Selection & Sync (2 minutes)
```
1. Select Instagram account (auto-selected if only one)
2. Select catalog (auto-selected if only one)
3. Click [Save & Sync Products]
4. Wait for sync to complete
```

### 5️⃣ Done! ✅
```
✅ Products live on Instagram Shop
✅ Can view sync status anytime
✅ Can re-sync on demand
```

**Total Time: ~10 minutes**

---

## Troubleshooting Quick Reference

| Error | Fix |
|-------|-----|
| "meta_app_id not configured" | Run SQL setup script |
| "Invalid authorization code" | Clear cookies, try again |
| "Instagram account not found" | Verify Business Manager access |
| "Products not syncing" | Check product_dir_token, view sync errors |
| OAuth callback blank | Check console errors, verify backend accessible |

---

## Testing Without Frontend

Use Postman Collection: `Instagram-API.postman_collection.json`

Steps:
1. Import collection into Postman
2. Set user_id variable
3. Run requests in order:
   - Start OAuth
   - OAuth Callback (manual)
   - Check Status
   - Get Config
   - Start Sync
   - View History

---

## Production Deployment

- [ ] Update Meta App OAuth URIs to production domain
- [ ] Update database oauth_redirect_uri to production
- [ ] Enable HTTPS
- [ ] Set `NODE_ENV=production` in backend
- [ ] Configure database backups
- [ ] Monitor sync errors via logs
- [ ] Set up alerts for sync failures

---

## Support

**Common Issues:**
- See INSTAGRAM_SETUP_GUIDE.md
- Check backend logs: `tail -f /var/log/instagram_business/app.log`
- Query database for errors: See `setup-instagram.sql` troubleshooting queries

**API Documentation:**
- Endpoint reference in INSTAGRAM_SETUP_GUIDE.md
- Full code docs in `index.py` (700+ lines, well-commented)

---

**Ready? Start at Phase 1 of INSTAGRAM_SETUP_GUIDE.md → then use this checklist!**
