# Production Deployment Guide

## Instagram Business Commerce Platform - Production Setup

---

## 1. Environment Configuration

### Backend (.env.production)

```bash
# Database - Production PostgreSQL
DB_HOST='your-production-db.rds.amazonaws.com'
DB_PORT='5432'
DB_USERNAME='prod_user'
DB_PASSWORD='STRONG_PASSWORD'
DB_DATABASE='instagram_business_prod'
DATABASE_URL="postgresql+asyncpg://prod_user:PASSWORD@host:5432/db"

# Environment
NODE_ENV='production'
PORT='8000'

# Security Keys (Generate NEW keys for production)
RSA_PUBLIC_KEY_BASE_64='NEW_PRODUCTION_PUBLIC_KEY'
RSA_PRIVATE_KEY_BASE_64='NEW_PRODUCTION_PRIVATE_KEY'
SECRET_FOR_COOKIES_SIGN='RANDOM_64_CHAR_STRING'

# Meta App (Production App)
META_APP_ID='your_meta_app_id'
META_APP_SECRET='your_meta_app_secret'
META_OAUTH_REDIRECT_URI='https://yourdomain.com/oauth/callback'

# Security
ALLOWED_ORIGINS='https://yourdomain.com'
RATE_LIMIT_PER_MINUTE='60'
ENABLE_RATE_LIMITING='true'

# Logging
LOG_LEVEL='INFO'
LOG_FILE_PATH='/var/log/instagram_business/app.log'

# JWT Tokens
JWT_EXPIRE_MINUTES='60'  # 1 hour
JWT_REFRESH_EXPIRE_DAYS='30'
```

### Frontend (.env.production)

```bash
VITE_ENV='prod'
VITE_API_BASE_URL='https://api.yourdomain.com/client/api/i/ona/x'
VITE_PUBLIC_API_BASE_URL='https://api.yourdomain.com/client-public/api/i'
VITE_UTILITY_ID='705'
VITE_PROJECT_NAME='ona'
VITE_INSTANCE_NAME='x'
```

---

## 2. Database Setup

### PostgreSQL Production Configuration

```sql
-- Create production database
CREATE DATABASE instagram_business_prod;

-- Create production user with limited privileges
CREATE USER prod_user WITH PASSWORD 'STRONG_PASSWORD';

-- Grant necessary permissions
GRANT CONNECT ON DATABASE instagram_business_prod TO prod_user;
GRANT USAGE, CREATE ON SCHEMA public TO prod_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO prod_user;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO prod_user;

-- Set default privileges for future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA public 
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO prod_user;
```

### Connection Pooling (Recommended)

Use PgBouncer or AWS RDS Proxy for connection pooling:

```ini
# pgbouncer.ini
[databases]
instagram_business = host=localhost dbname=instagram_business_prod

[pgbouncer]
pool_mode = transaction
max_client_conn = 1000
default_pool_size = 25
```

### Database Migration Script

```bash
# Run from backend directory
poetry run python -c "
from src.db_config import engine, Base
from src.shared.utility.l.0.705.index import InstagramBusiness, CatalogSyncHistory, CatalogSyncLog
import asyncio

async def migrate():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print('✓ Database tables created')

asyncio.run(migrate())
"
```

### Backup Strategy

```bash
# Daily backup cron job (add to crontab)
0 2 * * * pg_dump -U prod_user -h localhost instagram_business_prod | gzip > /backups/db_$(date +\%Y\%m\%d).sql.gz

# Keep last 30 days
0 3 * * * find /backups -name "db_*.sql.gz" -mtime +30 -delete
```

---

## 3. Security Configuration

### Generate New RSA Keys for Production

```bash
# Generate private key
openssl genrsa -out private_key.pem 2048

# Generate public key
openssl rsa -in private_key.pem -pubout -out public_key.pem

# Base64 encode for .env
cat private_key.pem | base64 -w 0
cat public_key.pem | base64 -w 0
```

### Generate Random Secret

```bash
# Generate 64-character random string
openssl rand -base64 48
```

### HTTPS Configuration

- Use Let's Encrypt for free SSL certificates
- Configure nginx/Apache as reverse proxy with SSL
- Enable HSTS headers

```nginx
# nginx example
server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;
    
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## 4. Meta App Configuration

### Create Production Meta App

1. Go to https://developers.facebook.com/apps
2. Create New App → Business Type
3. Add Products:
   - Instagram Basic Display
   - Instagram Graph API
   - Facebook Login

### Configure OAuth Settings

**Valid OAuth Redirect URIs:**
```
https://yourdomain.com/oauth/callback
https://www.yourdomain.com/oauth/callback
```

### Required Permissions

Request these permissions during app review:
- `instagram_basic`
- `instagram_content_publish`
- `instagram_manage_insights`
- `pages_show_list`
- `pages_read_engagement`
- `catalog_management`
- `business_management`

### App Review Submission

1. Complete Business Verification
2. Provide demo video showing OAuth flow
3. Add test users for Meta review team
4. Provide Privacy Policy URL
5. Provide Terms of Service URL
6. Submit for review (typically 1-5 business days)

### Update App Configuration in Database

```sql
-- Update instance config with production Meta App
UPDATE utility_instance 
SET data = jsonb_set(
    data, 
    '{config}',
    jsonb_build_object(
        'meta_app_id', 'YOUR_PRODUCTION_APP_ID',
        'meta_app_secret', 'YOUR_PRODUCTION_APP_SECRET',
        'oauth_redirect_uri', 'https://yourdomain.com/oauth/callback',
        'database', data->'config'->'database'
    )
)
WHERE utility_id = 705;
```

---

## 5. Error Handling & Logging

### Log Monitoring

Structured JSON logs are written to:
- Console (stdout) - All levels
- File (production) - INFO and above
- Location: `/var/log/instagram_business/app.log`

### Log Rotation

Automatic rotation:
- Max file size: 10MB
- Keep 10 backup files
- Total ~100MB log storage

### Error Tracking (Optional)

Integrate Sentry for error tracking:

```bash
# Install Sentry SDK
poetry add sentry-sdk

# Add to .env.production
ENABLE_SENTRY='true'
SENTRY_DSN='your_sentry_dsn'
```

```python
# Add to src/index.py
import sentry_sdk
import os

if os.getenv('ENABLE_SENTRY') == 'true':
    sentry_sdk.init(
        dsn=os.getenv('SENTRY_DSN'),
        environment=os.getenv('NODE_ENV', 'production'),
        traces_sample_rate=0.1
    )
```

---

## 6. Performance Optimization

### Database Indexing

```sql
-- Add indexes for frequently queried fields
CREATE INDEX idx_instagram_business_user_id ON instagram_business(user_id);
CREATE INDEX idx_catalog_sync_history_business_id ON catalog_sync_history(business_id);
CREATE INDEX idx_catalog_sync_log_sync_id ON catalog_sync_log(sync_id);
CREATE INDEX idx_catalog_sync_log_status ON catalog_sync_log(status);
```

### Connection Pool Configuration

```python
# src/db_config.py
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_size=20,        # Default connections
    max_overflow=10,     # Extra connections under load
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=3600    # Recycle connections every hour
)
```

### Caching (Optional)

Add Redis for caching Meta API responses:

```bash
# Install Redis support
poetry add redis aioredis
```

---

## 7. Token Management

### Production Token Generation

Use token_manager for production tokens:

```python
from src.shared.util.token_manager.index import TokenManager

# Create access + refresh token pair
access_token = TokenManager.create_access_token(
    user_id="seller_id",
    name="Seller Name"
)

refresh_token = TokenManager.create_refresh_token(
    user_id="seller_id"
)
```

### Frontend Token Refresh

Update frontend to handle token refresh:

```typescript
// Add to auth.helper.ts
async function refreshTokenIfNeeded() {
  const token = getJwtToken();
  if (!token) return;
  
  // Decode and check expiry
  const payload = JSON.parse(atob(token.split('.')[1]));
  const exp = payload.exp * 1000;
  const now = Date.now();
  
  // Refresh if expires in < 10 minutes
  if (exp - now < 10 * 60 * 1000) {
    const refreshToken = localStorage.getItem('refresh_token');
    const response = await fetch('/api/auth/refresh', {
      method: 'POST',
      body: JSON.stringify({ refresh_token: refreshToken })
    });
    const data = await response.json();
    setJwtToken(data.access_token);
  }
}
```

---

## 8. Health Checks & Monitoring

### Add Health Check Endpoint

```python
# Add to backend routing
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "1.0.0"
    }

@app.get("/readiness")
async def readiness_check():
    # Check database connection
    try:
        async with AsyncSession(engine) as db:
            await db.execute(text("SELECT 1"))
        return {"status": "ready"}
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={"status": "not_ready", "error": str(e)}
        )
```

### Monitoring Metrics

Track these metrics:
- Request rate (requests/minute)
- Error rate (%)
- Response time (p50, p95, p99)
- Database connection pool usage
- Meta API call success rate
- Sync job completion rate

---

## 9. Pre-Production Checklist

### Security
- [ ] New RSA keys generated
- [ ] Strong database password set
- [ ] CORS configured for production domain only
- [ ] Rate limiting enabled
- [ ] HTTPS/SSL configured
- [ ] Input validation active

### Database
- [ ] Production database created
- [ ] User permissions configured
- [ ] Tables migrated
- [ ] Indexes created
- [ ] Backup cron job configured

### Meta App
- [ ] Production app created
- [ ] OAuth redirect URIs configured
- [ ] Permissions requested
- [ ] App review submitted
- [ ] Business verification completed

### Configuration
- [ ] .env.production populated
- [ ] Frontend .env.production configured
- [ ] Log directory created with permissions
- [ ] Environment variables validated

### Testing
- [ ] OAuth flow tested
- [ ] Catalog sync tested
- [ ] Error handling tested
- [ ] Token refresh tested
- [ ] Rate limiting tested

---

## 10. Launch Procedure

1. **Database Migration**
   ```bash
   # Run migration script
   poetry run python migrate_production.py
   ```

2. **Start Backend**
   ```bash
   # With production env
   export $(cat .env.production | xargs)
   poetry run uvicorn src.index:app --host 0.0.0.0 --port 8000 --workers 4
   ```

3. **Build Frontend**
   ```bash
   cd Insta_business_frontend/Insta_business
   npm run build
   ```

4. **Verify Health**
   ```bash
   curl https://api.yourdomain.com/health
   curl https://api.yourdomain.com/readiness
   ```

5. **Monitor Logs**
   ```bash
   tail -f /var/log/instagram_business/app.log
   ```

---

## 11. Post-Launch Monitoring

### Week 1
- Monitor error rates daily
- Check Meta API rate limits
- Review sync success rates
- Validate token refresh working
- Check database performance

### Ongoing
- Weekly log reviews
- Monthly security audits
- Database backup verification
- Meta App compliance review
- Performance optimization

---

## Support & Troubleshooting

### Common Issues

**OAuth fails in production:**
- Verify redirect URI matches Meta App config exactly
- Check HTTPS is enabled
- Validate Meta App is in Live mode

**High database connection count:**
- Reduce pool_size in db_config
- Add PgBouncer connection pooler
- Check for connection leaks

**Rate limiting too aggressive:**
- Adjust RATE_LIMIT_PER_MINUTE in .env
- Implement user-specific limits
- Add Redis for distributed rate limiting

**Token refresh issues:**
- Verify JWT_EXPIRE_MINUTES is set
- Check clock sync on server
- Validate RSA keys match public/private pair

---

## Security Best Practices

1. **Never commit** .env.production to git
2. **Rotate** RSA keys every 6 months
3. **Review** Meta permissions regularly
4. **Monitor** failed login attempts
5. **Update** dependencies monthly
6. **Audit** database access logs
7. **Test** disaster recovery quarterly

---

**Production Ready Checklist Complete ✓**

Your Instagram Business Commerce platform is now production-ready with:
- ✅ Secure token management
- ✅ Environment-based CORS
- ✅ Rate limiting protection
- ✅ Structured logging
- ✅ Input validation
- ✅ Database optimization
- ✅ Error tracking capability
- ✅ Health monitoring
- ✅ Meta App production config

Next: Deploy and monitor! 🚀
