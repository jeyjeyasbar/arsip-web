# Quick Start: Deploy ARSIP Web Gratis Online

## Pilihan Hosting Gratis Terbaik

### 🥇 Railway (Rekomendasi)
- ✅ $5 free credit/bulan
- ✅ Tidak auto-sleep
- ✅ Setup 5 menit
- ✅ PostgreSQL included
- Link: https://railway.app

### 🥈 Render
- ✅ Benar-benar gratis (forever)
- ⚠️ Auto-sleep 15 menit (slow start)
- ✅ Setup 10 menit
- ✅ PostgreSQL free 90 hari
- Link: https://render.com

---

## Quick Start Railway (Recommended)

### 1. Push ke GitHub (2 menit)

```bash
cd C:\ArsipWebv10\ArsipWeb
git init
git add .
git commit -m "Deploy ARSIP"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/arsip-web.git
git push -u origin main
```

### 2. Create Railway Account (1 menit)

Buka https://railway.app → "Login with GitHub"

### 3. Deploy Project (2 menit)

1. Di Railway: "New Project" → "Deploy from GitHub repo"
2. Pilih `arsip-web`
3. Klik "Deploy Now"
4. Tambah PostgreSQL: "+ Add" → "PostgreSQL"

### 4. Set Environment Variables (2 menit)

Di Railway project, tab **Variables**:

```
APP_ENV=production
SECRET_KEY=abcd1234...xyz (64 chars, generate: python -c "import secrets; print(secrets.token_hex(32))")
COOKIE_SECURE=true
FRONTEND_URL=https://arsip-web-prod.railway.app
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=arsip.chici@gmail.com
SMTP_PASSWORD=nrfhwjlsvszridhy
SMTP_FROM=arsip.chici@gmail.com
SMTP_TLS=true
```

### 5. Initialize Database (1 menit)

Di Railway deployment shell:

```bash
python -c "from app import create_app; from app.models import db; app = create_app(); app.app_context().push(); db.create_all(); print('✅ DB ready')"
```

### 6. Test (1 menit)

```bash
curl https://YOUR-RAILWAY-URL.railway.app/health
```

Expected: `{"status":"ok"}`

---

## Total Time: ~15 menit

Aplikasi Anda sudah online! 🎉

---

## File-File Penting untuk Deploy

Sudah ada di project:

- ✅ `Procfile` - cara Railway jalankan app
- ✅ `runtime.txt` - Python version
- ✅ `requirements.txt` - dependencies
- ✅ `wsgi.py` - entry point
- ✅ `.gitignore` - hide .env & secrets

---

## Dokumentasi Lengkap

- [DEPLOY_RAILWAY_FREE.md](DEPLOY_RAILWAY_FREE.md) - Step-by-step Railway
- [DEPLOY_RENDER_FREE.md](DEPLOY_RENDER_FREE.md) - Step-by-step Render
- [PRODUCTION_DEPLOYMENT.md](PRODUCTION_DEPLOYMENT.md) - Production setup

---

## Troubleshoot

### Deploy failed?

Check Railway logs:
- Project → Deployments → Latest → View Logs

### Database error?

Pastikan PostgreSQL service:
- Started (tab Services, lihat status)
- DATABASE_URL tidak override (auto-set oleh Railway)

### Email tidak terkirim?

Pastikan:
- `SMTP_PASSWORD=nrfhwjlsvszridhy` (16 chars, no spaces)
- `SMTP_HOST=smtp.gmail.com`
- `SMTP_PORT=587`

---

## Budget per Bulan

- **Railway**: $0-20 (depending on usage, $5 free credit/month)
- **Render**: $0 (free tier) atau $16+ (paid)

For 100 users/day → ~$10-15 Railway

---

## Next Steps

1. Generate SECRET_KEY → deploy Railway
2. Setup custom domain (optional)
3. Monitor logs
4. Share URL dengan users

URL akan seperti: **https://arsip-web-prod-xxx.railway.app**

---

Ready? Let's go! 🚀
