# Production Deployment Guide

## Overview

Aplikasi ARSIP Web sudah dipersiapkan untuk production dengan:
- ✅ Secure authentication (JWT + refresh tokens)
- ✅ Email verification required before login
- ✅ Password reset via email (dengan Gmail SMTP fallback SSL)
- ✅ File upload validation & ownership checks
- ✅ HTTPS-ready cookie configuration
- ✅ PostgreSQL support

---

## Pre-Deployment Checklist

### 1. Environment Variables (`.env`)

#### Required Changes for Production:

```env
APP_ENV=production
SECRET_KEY=<generate-random-64-char-hex>
COOKIE_SECURE=true
DATABASE_URL=postgresql+psycopg://user:password@host:5432/arsip_db
FRONTEND_URL=https://your-domain.com
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-gmail@gmail.com
SMTP_PASSWORD=<gmail-app-password>
```

#### How to Generate Secure SECRET_KEY:

Windows PowerShell:
```powershell
[System.BitConverter]::ToString([System.Security.Cryptography.RNGCryptoServiceProvider]::new().GetBytes(32)) -replace '-'
```

Or Python:
```python
import secrets
print(secrets.token_hex(32))
```

---

### 2. Database Setup (PostgreSQL)

If using PostgreSQL instead of SQLite:

```bash
# Create database
createdb arsip_db

# Run migrations (if schema changes are tracked)
# For now, Flask-SQLAlchemy will auto-create tables on first run
```

Connection string format:
```
postgresql+psycopg://username:password@localhost:5432/arsip_db
```

---

### 3. SMTP Configuration

#### Gmail App Password (Recommended)

1. Enable 2FA on Gmail account
2. Generate App Password: https://myaccount.google.com/apppasswords
3. Use that 16-character password (remove spaces) in `SMTP_PASSWORD`

**Note:** The app now supports both STARTTLS (port 587) and SSL (port 465) fallback.

---

### 4. SSL/TLS Certificate

Set up HTTPS on your production server:

- Use reverse proxy (Nginx/Apache) with SSL cert (Let's Encrypt recommended)
- Ensure `COOKIE_SECURE=true` is set in `.env` (cookies only sent over HTTPS)
- Configure `FRONTEND_URL=https://your-domain.com` (no trailing slash)

---

### 5. File Upload Directory

Ensure the `UPLOAD_FOLDER` directory has:
- Proper write permissions for app process
- Regular backups configured
- Sufficient disk space

```bash
mkdir -p /var/uploads/arsip
chmod 755 /var/uploads/arsip
chown appuser:appuser /var/uploads/arsip
```

---

### 6. Application Server (Gunicorn)

Start the app with Gunicorn:

```bash
gunicorn --workers 4 --bind 0.0.0.0:5000 wsgi:app
```

Or with Nginx as reverse proxy:

```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }
}
```

---

### 7. Security Hardening

#### Disable Development Fallbacks

The app currently returns dev verification/reset tokens in `APP_ENV=development` for testing. In production:
- ✅ These fallbacks are **automatically disabled** when `APP_ENV=production`
- Users **must** use real email verification
- Password reset links are sent **only via email**

#### Other Security Measures

- [ ] Enable CORS restrictions (currently allows all in dev)
- [ ] Implement rate limiting on `/api/auth/*` endpoints
- [ ] Set up monitoring & logging
- [ ] Regular security audits & dependency updates

---

### 8. Deployment Validation

After deploying to production:

```bash
# Test health endpoint
curl https://your-domain.com/health

# Test registration (verify email is sent)
curl -X POST https://your-domain.com/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name":"Test","email":"test@example.com","password":"securepass123"}'

# Verify dev_verify_token is NOT returned
```

---

## Environment-Specific Behavior

### Development (`APP_ENV=development`)

- ✅ Returns `dev_verify_token` for quick testing
- ✅ Returns `dev_reset_token` for password reset testing
- ✅ Allows `COOKIE_SECURE=false`
- ✅ Supports SQLite

### Production (`APP_ENV=production`)

- ❌ **No** dev tokens returned
- ✅ Email verification **required** before login
- ✅ Password reset **only via email**
- ✅ Requires `COOKIE_SECURE=true`
- ✅ Requires real SMTP configuration

---

## Troubleshooting

### Email not sending in production?

1. Verify `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD` are correct
2. Ensure Gmail App Password is used (not main password)
3. Check server firewall allows outbound 587 or 465
4. Check application logs for SMTP errors

### Database connection failed?

1. Verify `DATABASE_URL` format (postgres**ql** not postgres)
2. Ensure database exists and user has permissions
3. Test connection manually: `psql -c "SELECT 1"`

### Cookies not persisting?

1. Ensure `COOKIE_SECURE=true` and using HTTPS
2. Verify `FRONTEND_URL` matches browser URL

---

## Backup & Maintenance

- **Database:** Schedule daily backups of PostgreSQL
- **Uploads:** Archive old uploads regularly
- **Logs:** Implement log rotation
- **Dependencies:** Review `requirements.txt` monthly for security updates

---

## Support

For questions or issues during deployment, refer to:
- Flask: https://flask.palletsprojects.com
- SQLAlchemy: https://docs.sqlalchemy.org
- Gunicorn: https://gunicorn.org
