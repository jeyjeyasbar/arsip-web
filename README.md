# ARSIP! Full Stack v3

Aplikasi arsip mahasiswa: pembayaran, kegiatan, dokumen, akun, profil, autentikasi email, reset password.

## Fitur
- Login/register email + password
- Refresh token HttpOnly cookie + access JWT
- Logout dan session invalidation
- Lupa password via email reset
- Profil dan foto profil
- CRUD pembayaran, kegiatan, dokumen, akun
- Upload JPG/JPEG/PNG/WEBP/PDF dengan validasi dasar
- Enkripsi password akun layanan menggunakan Fernet
- SQLite development / PostgreSQL production
- Docker + Gunicorn

## Local
1. Buat virtual environment.
2. `pip install -r requirements.txt`
3. Copy `.env.example` menjadi `.env`.
4. Generate encryption key:
   `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`
5. Masukkan key ke `APP_ENCRYPTION_KEY`.
6. Jalankan `python run.py`.
7. Buka `http://127.0.0.1:5000`.

## Production
Gunakan PostgreSQL dan set:
- `APP_ENV=production`
- `SECRET_KEY` random panjang
- `APP_ENCRYPTION_KEY` dari Fernet
- `DATABASE_URL=postgresql+psycopg://...`
- `FRONTEND_URL=https://domain-anda`
- `COOKIE_SECURE=true`
- SMTP variables agar reset password benar-benar mengirim email.

Docker:
`docker compose up --build -d`

## Reset password
Dalam development tanpa SMTP, endpoint forgot-password mengembalikan `dev_reset_token`. Dalam production token tidak dikembalikan ke client; SMTP harus dikonfigurasi.

## Catatan deployment
Untuk production serius, gunakan object storage (S3/R2/GCS) untuk file, HTTPS di reverse proxy, backup PostgreSQL, dan monitoring. Jangan commit `.env`.
