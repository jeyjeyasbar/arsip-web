import os,re
from pathlib import Path
from dotenv import load_dotenv
BASE_DIR=Path(__file__).resolve().parent; load_dotenv(BASE_DIR/'.env')

def _abs_path(p):
    """Jadikan path absolut berbasis lokasi project (BASE_DIR), supaya tidak
    tergantung current working directory saat aplikasi dijalankan (mis. lewat
    IDE, shortcut, atau service yang cwd-nya beda dari folder project)."""
    p=str(p)
    if os.path.isabs(p) or re.match(r'^[A-Za-z]:[\\/]',p):return p
    return str((BASE_DIR/p).resolve())

class Config:
    SECRET_KEY=os.getenv('SECRET_KEY','dev-only-change-me'); APP_ENCRYPTION_KEY=os.getenv('APP_ENCRYPTION_KEY','')
    DATABASE_URL=os.getenv('DATABASE_URL',f"sqlite:///{BASE_DIR/'instance'/'arsip.db'}")
    if DATABASE_URL.startswith('postgres://'): DATABASE_URL='postgresql+psycopg://'+DATABASE_URL[11:]
    elif DATABASE_URL.startswith('postgresql://'): DATABASE_URL='postgresql+psycopg://'+DATABASE_URL[13:]
    elif DATABASE_URL.startswith('sqlite:///') and DATABASE_URL not in ('sqlite:///:memory:',):
        DATABASE_URL='sqlite:///'+_abs_path(DATABASE_URL[len('sqlite:///'):])
    SQLALCHEMY_DATABASE_URI=DATABASE_URL; SQLALCHEMY_TRACK_MODIFICATIONS=False
    FRONTEND_URL=os.getenv('FRONTEND_URL','http://127.0.0.1:5000')
    UPLOAD_FOLDER=_abs_path(os.getenv('UPLOAD_FOLDER',str(BASE_DIR/'uploads'))); MAX_CONTENT_LENGTH=int(os.getenv('MAX_UPLOAD_MB','10'))*1024*1024
    ACCESS_TOKEN_MINUTES=int(os.getenv('ACCESS_TOKEN_MINUTES','15')); REFRESH_TOKEN_DAYS=int(os.getenv('REFRESH_TOKEN_DAYS','30'))
    SMTP_HOST=os.getenv('SMTP_HOST',''); SMTP_PORT=int(os.getenv('SMTP_PORT','587')); SMTP_USER=os.getenv('SMTP_USER',''); SMTP_PASSWORD=os.getenv('SMTP_PASSWORD',''); SMTP_FROM=os.getenv('SMTP_FROM',SMTP_USER); SMTP_TLS=os.getenv('SMTP_TLS','true').lower()=='true'
    ENVIRONMENT=os.getenv('APP_ENV','development'); COOKIE_SECURE=os.getenv('COOKIE_SECURE','false').lower()=='true'