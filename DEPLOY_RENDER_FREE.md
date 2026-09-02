# Deploy ARSIP Web ke Render (Free Tier)

## Overview

Render menawarkan:
- ✅ Free tier untuk Flask apps
- ✅ PostgreSQL database gratis 90 hari
- ✅ Auto-sleep setelah 15 menit inactivity (normal untuk free)
- ✅ HTTPS otomatis
- ✅ GitHub integration mudah

---

## Step 1: Siapkan Repository di GitHub

### 1a. Buat GitHub Repository

1. Buka https://github.com/new
2. Repository name: `arsip-web` (atau nama lain)
3. Public (agar Render bisa akses)
4. Klik "Create repository"

### 1b. Push kode ke GitHub

```bash
cd C:\ArsipWebv10\ArsipWeb
git init
git add .
git commit -m "Initial commit: ARSIP Web production-ready"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/arsip-web.git
git push -u origin main
```

**Catatan:** Ganti `YOUR-USERNAME` dengan GitHub username Anda.

---

## Step 2: Siapkan File Konfigurasi untuk Render

### 2a. Buat `Procfile` (di root project)

```
web: gunicorn --workers 1 --bind 0.0.0.0:$PORT wsgi:app
```

File ini mengatakan ke Render bagaimana menjalankan aplikasi.

### 2b. Pastikan `requirements.txt` sudah lengkap

Cek bahwa semua dependency ada:

```
Flask==3.1.2
Flask-Cors==6.0.1
Flask-SQLAlchemy==3.1.1
PyJWT==2.10.1
python-dotenv==1.1.1
psycopg[binary]==3.2.9
cryptography==45.0.7
Pillow==11.3.0
gunicorn==23.0.0
pytest==8.4.2
```

### 2c. Buat `.gitignore` (agar `.env` tidak ke-push)

```
.env
.env.production
__pycache__/
*.pyc
instance/
uploads/
```

---

## Step 3: Deploy ke Render

### 3a. Daftar Render

1. Buka https://render.com
2. Klik "Get Started" → Sign up with GitHub
3. Authorize Render untuk akses GitHub

### 3b. Buat Web Service Baru

1. Di Render dashboard, klik "+ New"
2. Pilih "Web Service"
3. Pilih repository `arsip-web` → klik "Connect"
4. Isi form:

   | Field | Value |
   |-------|-------|
   | **Name** | arsip-web |
   | **Environment** | Python 3 |
   | **Build Command** | `pip install -r requirements.txt` |
   | **Start Command** | `gunicorn --workers 1 --bind 0.0.0.0:$PORT wsgi:app` |
   | **Instance Type** | Free |

5. Klik "Create Web Service"

### 3c. Tambahkan PostgreSQL Database

1. Di Render dashboard, klik "+ New"
2. Pilih "PostgreSQL"
3. Isi form:

   | Field | Value |
   |-------|-------|
   | **Name** | arsip-db |
   | **Database** | arsip_db |
   | **User** | postgres |
   | **Instance Type** | Free |
   | **Region** | Singapore (atau pilih terdekat) |

4. Klik "Create Database"

---

## Step 4: Konfigurasi Environment Variables

### 4a. Di Render Dashboard - Web Service

1. Pilih web service `arsip-web`
2. Buka tab **Environment**
3. Tambahkan environment variables:

```
APP_ENV=production
SECRET_KEY=<GENERATE-64-HEX-CHARS-BARU>
COOKIE_SECURE=true
DATABASE_URL=<COPY-DARI-DATABASE-CREDENTIALS>
FRONTEND_URL=https://arsip-web.onrender.com
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

### 4b. Generate SECRET_KEY

Buka terminal Python:

```python
import secrets
print(secrets.token_hex(32))
```

Hasil: `abcd1234...` (64 karakter) → copy ke `SECRET_KEY`

### 4c. Copy DATABASE_URL dari PostgreSQL Database

1. Buka PostgreSQL database di Render (`arsip-db`)
2. Tab **Connections**
3. Copy **Internal Database URL** (dimulai dengan `postgresql://`)
4. Paste ke `DATABASE_URL` di Web Service environment

Contoh:
```
postgresql+psycopg://postgres:xxxxx@dpg-xxxxx.onrender.com/arsip_db
```

---

## Step 5: Jalankan Database Migration

Setelah deploy berhasil:

1. Buka **arsip-web** service di Render
2. Tab **Shell**
3. Jalankan:

```bash
python -c "from app import create_app; from app.models import db; app = create_app(); app.app_context().push(); db.create_all(); print('✅ Database initialized')"
```

Jika output: `✅ Database initialized` → OK

---

## Step 6: Testing Aplikasi Online

Cek apakah aplikasi sudah live:

```bash
curl https://arsip-web.onrender.com/health
```

Expected output:
```json
{"status":"ok"}
```

Test register user:

```bash
curl -X POST https://arsip-web.onrender.com/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "password": "securepass123"
  }'
```

Expected: `403` error (email verification required di production)

---

## Step 7: Setup Custom Domain (Opsional)

### Jika Anda punya domain sendiri:

1. Di Render - Web Service `arsip-web`
2. Tab **Settings**
3. Cari "Custom Domains"
4. Masukkan domain: `arsip.example.com` (atau main domain)
5. Render akan generate DNS records
6. Update DNS di domain registrar Anda

---

## Troubleshooting

### Aplikasi error saat deploy?

1. Buka tab **Logs** di Render
2. Cek error message
3. Common issues:
   - `ModuleNotFoundError` → pastikan `requirements.txt` lengkap
   - `DATABASE_URL invalid` → pastikan format `postgresql+psycopg://...`
   - `SECRET_KEY not set` → tambahkan di Environment tab

### Email tidak terkirim?

- Pastikan `SMTP_PASSWORD` benar (gunakan 16-char App Password)
- Cek Render logs untuk SMTP errors
- Pastikan `SMTP_HOST=smtp.gmail.com` dan `SMTP_PORT=587`

### Upload file gagal?

- Free tier Render tidak punya persistent storage
- File yang di-upload akan hilang saat app restart
- Solusi: gunakan cloud storage (AWS S3, Google Cloud Storage) → lebih advanced

### Database connection timeout?

- Pastikan `DATABASE_URL` sudah diupdate di Environment
- Tunggu 2-3 menit setelah PostgreSQL database dibuat
- Restart web service di Render dashboard

---

## Database Auto-Sleep (Free Tier)

Dengan free tier:
- Web service **auto-sleep** setelah 15 menit inactivity
- Akses pertama setelah sleep akan **slow** (~30 detik)
- Database **tidak auto-sleep**

Untuk production-grade reliability → upgrade ke paid tier

---

## Next Steps

### Upgrade ke Paid (Jika perlu):

1. **Web Service:** $7/bulan → always active
2. **PostgreSQL:** $9/bulan → better performance

Total: ~$16/bulan untuk production-ready

### Atau coba alternatif gratis:

- **Railway** - $5 free credit per bulan
- **PythonAnywhere** - free tier terbatas

---

## Checklist Deployment

- [ ] GitHub repo created & code pushed
- [ ] Procfile & requirements.txt siap
- [ ] Render account dibuat
- [ ] Web Service created (arsip-web)
- [ ] PostgreSQL created (arsip-db)
- [ ] Environment variables diisi
- [ ] DATABASE_URL di-copy dengan benar
- [ ] Database migration dijalankan (`db.create_all()`)
- [ ] Health endpoint tested (`/health`)
- [ ] Register endpoint tested
- [ ] Domain configuration (opsional)

---

## URL Aplikasi Anda

Setelah deployment selesai:
```
https://arsip-web.onrender.com
```

Ganti `arsip-web` dengan nama service yang Anda buat di Render.
