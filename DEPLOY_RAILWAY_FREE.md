# Deploy ARSIP Web ke Railway (Alternatif Gratis dengan $5 Credit)

## Overview

Railway menawarkan:
- ✅ $5 free credit per bulan (cukup untuk starter)
- ✅ PostgreSQL database gratis dalam credit limit
- ✅ Python/Flask support native
- ✅ GitHub integration instant
- ✅ HTTPS otomatis
- ✅ Tidak auto-sleep (selama ada credit)

---

## Step 1: Persiapkan Repository GitHub

Sama seperti Render:

```bash
cd C:\ArsipWebv10\ArsipWeb
git init
git add .
git commit -m "Initial commit: ARSIP Web production"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/arsip-web.git
git push -u origin main
```

---

## Step 2: Pastikan Procfile & runtime.txt Ada

**Procfile** (di root):
```
web: gunicorn --workers 1 --bind 0.0.0.0:$PORT wsgi:app
```

**runtime.txt** (di root):
```
python-3.12.10
```

---

## Step 3: Deploy ke Railway

### 3a. Daftar Railway

1. Buka https://railway.app
2. Klik "Login with GitHub" atau "Start Project"
3. Authorize Railway untuk GitHub

### 3b. Buat Project Baru

1. Di Railway dashboard, klik "Create New Project"
2. Pilih "Deploy from GitHub repo"
3. Pilih repository `arsip-web`
4. Klik "Deploy Now"

Railway akan:
- Detect Python automatically
- Install `requirements.txt`
- Jalankan `Procfile`

### 3c. Tambah PostgreSQL Database

1. Di project Railway
2. Klik "+ Add" → Database
3. Pilih "PostgreSQL"
4. Klik "Create"

Railway otomatis generate `DATABASE_URL` environment variable.

---

## Step 4: Konfigurasi Environment Variables

### 4a. Di Railway Project Settings

1. Klik project `arsip-web`
2. Tab **Variables**
3. Tambahkan:

```
APP_ENV=production
SECRET_KEY=<GENERATE-64-HEX-CHARS>
COOKIE_SECURE=true
FRONTEND_URL=https://YOUR-RAILWAY-URL.railway.app
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=arsip.chici@gmail.com
SMTP_PASSWORD=nrfhwjlsvszridhy
SMTP_FROM=arsip.chici@gmail.com
SMTP_TLS=true
UPLOAD_FOLDER=/tmp/uploads
MAX_UPLOAD_MB=10
ACCESS_TOKEN_MINUTES=15
REFRESH_TOKEN_DAYS=30
```

**Catatan:** Railway otomatis set `DATABASE_URL` dari PostgreSQL service, jangan override.

### 4b. Generate SECRET_KEY

```python
import secrets
print(secrets.token_hex(32))
```

---

## Step 5: Database Initialization

Setelah deployment:

1. Di Railway, klik project
2. Tab **Deployments** → Latest deployment
3. Klik **Shell** icon
4. Jalankan:

```bash
python -c "from app import create_app; from app.models import db; app = create_app(); app.app_context().push(); db.create_all(); print('✅ Database initialized')"
```

---

## Step 6: Test Aplikasi

Dapatkan URL dari Railway:

Buka tab **Settings** → cari "Railway Provided Domain"

Contoh: `https://arsip-web-production-xxx.railway.app`

Test:
```bash
curl https://YOUR-URL.railway.app/health
```

---

## Billing & Limits

Railway credit system:
- **$5 free per bulan** (auto-refresh)
- Typical usage:
  - Web dyno: ~$0.10/day
  - PostgreSQL: ~$10/month

Jika melebihi $5:
- Layanan tidak auto-stop
- Tagihan di akhir bulan
- Bisa set spending limit di settings

---

## Render vs Railway Comparison

| Feature | Render (Free) | Railway ($5 credit) |
|---------|---------------|--------------------|
| **Always On** | ❌ (auto-sleep) | ✅ (cepat) |
| **Database** | PostgreSQL free 90 hari | PostgreSQL dalam credit |
| **Monthly Cost** | Gratis | ~$10-20 (if >credit) |
| **Startup Speed** | Slow (15min sleep) | Fast |
| **Custom Domain** | ✅ | ✅ |
| **Ease of Use** | Medium | Easy |

**Rekomendasi:** Gunakan Railway jika ingin tanpa auto-sleep dalam budget $5/bulan.

---

## Troubleshooting

### Database tidak bisa connect?

Railway otomatis set `DATABASE_URL`. Pastikan:
- PostgreSQL service sudah "Started"
- Tidak override `DATABASE_URL` di Variables
- Tunggu 1-2 menit setelah PostgreSQL created

### Deployment gagal?

Cek Railway logs:
- Buka project
- Tab **Deployments**
- Click deployment → **View Logs**

Common errors:
- `requirements.txt not found` → pastikan di root
- `gunicorn not installed` → tambahkan ke requirements.txt
- `Module not found` → pastikan semua import ada di requirements.txt

### Aplikasi restart terus-menerus?

Cek di Railway Logs:
- Biasanya crash karena environment variable missing
- Pastikan `DATABASE_URL` set dengan benar
- Pastikan `SECRET_KEY` tidak kosong

---

## Custom Domain (Opsional)

1. Di Railway, buka project settings
2. Cari "Custom Domain"
3. Masukkan domain: `arsip.example.com`
4. Railway generate DNS CNAME record
5. Update DNS di registrar (Namecheap, GoDaddy, dll)

---

## Upgrade Path

Jika traffic bertambah:
- Upgrade dari $5 credit → paid tier
- Database -> Production PostgreSQL
- Add Redis cache
- Multi-region deployment

Railway scaling mudah - tidak perlu ubah code.

---

## Checklist Deployment Railway

- [ ] GitHub repo created & pushed
- [ ] Procfile & runtime.txt ada di root
- [ ] Railway account created
- [ ] Project created dari GitHub
- [ ] PostgreSQL database added
- [ ] Environment variables diisi
- [ ] SECRET_KEY di-generate
- [ ] Database migration dijalankan
- [ ] Health endpoint tested
- [ ] Register tested
- [ ] Custom domain setup (opsional)

---

## URL Aplikasi Anda

```
https://YOUR-PROJECT-NAME.railway.app
```

Lihat di Railway dashboard untuk exact URL.
