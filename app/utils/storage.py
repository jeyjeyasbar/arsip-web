from pathlib import Path
from flask import current_app

def remove_file(rel_path):
    """Hapus file fisik di UPLOAD_FOLDER yang direferensikan oleh rel_path
    (mis. '/api/files/3_abcd1234.jpg'). Aman dipanggil dengan None/'' atau
    path yang tidak berasal dari folder upload kita."""
    if not rel_path:
        return
    rel_path = str(rel_path)
    if not rel_path.startswith('/api/files/'):
        return
    name = rel_path.rsplit('/', 1)[-1]
    if not name or '/' in name or '\\' in name:
        return
    p = Path(current_app.config['UPLOAD_FOLDER']) / name
    try:
        if p.is_file():
            p.unlink()
    except Exception:
        current_app.logger.exception('Gagal menghapus file %s', name)

def owner_id_from_filename(name):
    """Ekstrak id pemilik dari nama file yang dihasilkan saat upload.
    Pola: '{user_id}_{uuid}.ext' atau 'profile_{user_id}_{uuid}.ext'."""
    parts = (name or '').split('_')
    if not parts:
        return None
    if parts[0] == 'profile' and len(parts) > 1:
        parts = parts[1:]
    try:
        return int(parts[0])
    except (ValueError, IndexError):
        return None
