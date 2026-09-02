import os, base64
from cryptography.fernet import Fernet

def _fernet():
    key=os.getenv('APP_ENCRYPTION_KEY')
    if not key: raise RuntimeError('APP_ENCRYPTION_KEY belum dikonfigurasi')
    return Fernet(key.encode())

def encrypt(value): return _fernet().encrypt(value.encode()).decode()
def decrypt(value):
    try: return _fernet().decrypt(value.encode()).decode()
    except Exception: return ''
