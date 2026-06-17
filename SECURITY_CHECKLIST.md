# Production Security Checklist

## Instagram Business Commerce Platform - Security Audit

---

## ✅ Critical Security Items

### 1. Credentials & Keys

- [ ] **NEW RSA keys generated** (not using dev keys)
  ```bash
  openssl genrsa -out private_key.pem 2048
  openssl rsa -in private_key.pem -pubout -out public_key.pem
  ```

- [ ] **Database password** is strong (16+ chars, mixed case, numbers, symbols)

- [ ] **SECRET_FOR_COOKIES_SIGN** is random and unique
  ```bash
  openssl rand -base64 48
  ```

- [ ] **Meta App Secret** is secure and not exposed

- [ ] **.env.production** is NOT committed to git
  ```bash
  # Add to .gitignore
  .env.production
  ```

---

### 2. Network Security

- [ ] **HTTPS/SSL** enabled (no HTTP)
  - Certificate valid and not expired
  - Redirect HTTP → HTTPS
  - HSTS header enabled

- [ ] **CORS** restricted to production domains only
  ```python
  # In .env.production
  ALLOWED_ORIGINS='https://yourdomain.com'
  ```

- [ ] **Rate limiting** enabled
  ```python
  ENABLE_RATE_LIMITING='true'
  RATE_LIMIT_PER_MINUTE='60'
  ```

- [ ] **Firewall** configured
  - Allow: 443 (HTTPS), 22 (SSH - restricted IPs)
  - Deny: All other ports

---

### 3. Database Security

- [ ] **Database user** has minimal privileges (not superuser)
  ```sql
  GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES TO prod_user;
  ```

- [ ] **Database password** not in code (only in .env)

- [ ] **Database accessible only** from application server

- [ ] **Backups encrypted** and stored securely

- [ ] **SSL/TLS** enabled for database connections

---

### 4. Authentication & Authorization

- [ ] **JWT expiry** set to reasonable time (60 minutes)
  ```python
  JWT_EXPIRE_MINUTES='60'
  ```

- [ ] **Refresh tokens** implemented with 30-day expiry

- [ ] **Token validation** on every protected endpoint

- [ ] **User session** management implemented

---

### 5. Input Validation

- [ ] **All user inputs** validated and sanitized
  - User IDs
  - URLs
  - JSON payloads
  - Query parameters

- [ ] **SQL injection** protected (using parameterized queries)

- [ ] **XSS protection** (escaping user content)

- [ ] **File upload** restrictions (if applicable)

---

### 6. API Security

- [ ] **Rate limiting** per user/IP

- [ ] **Request size** limits enforced

- [ ] **Timeout** configuration on external API calls

- [ ] **Meta API credentials** stored securely

- [ ] **OAuth redirect URI** matches exactly

---

### 7. Logging & Monitoring

- [ ] **Sensitive data NOT logged** (passwords, tokens, secrets)

- [ ] **Failed login attempts** tracked

- [ ] **Suspicious activity** alerts configured

- [ ] **Log files** have restricted permissions
  ```bash
  chmod 600 /var/log/instagram_business/app.log
  ```

- [ ] **Log rotation** configured (prevent disk fill)

---

### 8. Error Handling

- [ ] **Stack traces** not exposed to users

- [ ] **Generic error messages** in production

- [ ] **Detailed errors** logged server-side only

- [ ] **500 errors** don't leak internal info

---

### 9. Dependencies

- [ ] **All packages** updated to latest secure versions
  ```bash
  poetry update
  ```

- [ ] **Vulnerability scan** run
  ```bash
  poetry run pip-audit
  ```

- [ ] **No dev dependencies** in production build

---

### 10. Meta App Security

- [ ] **Production Meta App** created (not using test app)

- [ ] **App is in Live mode** (not Development)

- [ ] **Permissions** reviewed and minimal

- [ ] **Webhook verification** implemented (if using webhooks)

- [ ] **App Secret** not exposed in client-side code

- [ ] **Business verification** completed

---

## 🔒 Additional Security Measures

### Code Security

- [ ] **Secrets not hardcoded** anywhere in code

- [ ] **Environment variables** used for all config

- [ ] **.git folder** not accessible via web

- [ ] **Debug mode** disabled in production
  ```python
  NODE_ENV='production'
  ```

### Server Security

- [ ] **OS and packages** updated

- [ ] **SSH key-only** authentication (no passwords)

- [ ] **Fail2ban** or similar intrusion prevention

- [ ] **Non-root user** runs application

- [ ] **Server timezone** set to UTC

### Application Security

- [ ] **CSRF protection** (if applicable)

- [ ] **Content Security Policy** headers

- [ ] **X-Frame-Options** header set

- [ ] **X-Content-Type-Options** header set

### Compliance

- [ ] **Privacy Policy** published and linked

- [ ] **Terms of Service** published

- [ ] **GDPR compliance** (if EU users)
  - Data deletion endpoint
  - Data export endpoint
  - User consent tracking

- [ ] **Meta Platform Terms** compliance

---

## 🔐 Security Testing

### Pre-Launch Tests

- [ ] **Penetration testing** performed

- [ ] **SQL injection** tests passed

- [ ] **XSS vulnerability** tests passed

- [ ] **CSRF** tests passed (if applicable)

- [ ] **Rate limiting** tested and working

- [ ] **Token expiry** tested

- [ ] **OAuth flow** security verified

### Ongoing Monitoring

- [ ] **Weekly security scans** scheduled

- [ ] **Monthly dependency audits** scheduled

- [ ] **Quarterly penetration tests** scheduled

- [ ] **Security incident response plan** documented

---

## 🚨 Incident Response Plan

### If Security Breach Detected

1. **Immediately**
   - Revoke all access tokens
   - Rotate all secrets (RSA keys, database passwords)
   - Enable maintenance mode

2. **Investigation**
   - Review logs for breach timeline
   - Identify compromised data
   - Determine attack vector

3. **Communication**
   - Notify affected users
   - Report to Meta if app credentials compromised
   - Document incident

4. **Recovery**
   - Patch vulnerability
   - Deploy security fix
   - Re-enable service

5. **Prevention**
   - Update security measures
   - Add monitoring for similar attacks
   - Conduct security review

---

## 📋 Monthly Security Checklist

- [ ] Review access logs for anomalies
- [ ] Update dependencies (`poetry update`)
- [ ] Run vulnerability scan (`pip-audit`)
- [ ] Review and rotate secrets (every 6 months)
- [ ] Check SSL certificate expiry
- [ ] Verify backup integrity
- [ ] Review rate limiting effectiveness
- [ ] Audit user permissions
- [ ] Check for new Meta API security guidelines

---

## 🛡️ Security Contacts

**Meta Security Issues:**
- Report: https://www.facebook.com/whitehat

**Database Provider:**
- AWS RDS Support: [Your support channel]

**Infrastructure:**
- [Your hosting provider support]

---

## Sign-Off

**Security Review Completed By:** ___________________

**Date:** ___________________

**Environment:** Production

**All Critical Items Checked:** YES / NO

**Approved for Production:** YES / NO

---

**Remember:** Security is ongoing, not a one-time task!

Review this checklist monthly and after any major changes.
