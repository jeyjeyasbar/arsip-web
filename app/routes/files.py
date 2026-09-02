import hashlib
from datetime import datetime,timezone
from pathlib import Path
from uuid import uuid4
import jwt
from flask import Blueprint,request,jsonify,current_app,send_from_directory
from app.models import RefreshSession
from app.utils.auth import require_auth
from app.utils.storage import owner_id_from_filename
bp=Blueprint('files',__name__)
ALLOWED={'jpg','jpeg','png','webp','pdf'}
def ext(n):return n.rsplit('.',1)[-1].lower() if '.' in n else ''
def _rh(v):return hashlib.sha256(v.encode()).hexdigest()
def _request_user_id():
 """Izinkan akses file lewat Authorization bearer ATAU refresh_token cookie."""
 auth=request.headers.get('Authorization','').strip()
 if auth.startswith('Bearer '):
  try:
   payload=jwt.decode(auth[7:],current_app.config['SECRET_KEY'],algorithms=['HS256'])
   if payload.get('type')=='access':
    return int(payload['sub'])
  except Exception:
   pass
 raw=request.cookies.get('refresh_token','')
 if not raw:return None
 s=RefreshSession.query.filter_by(token_hash=_rh(raw),revoked_at=None).first()
 if not s or s.expires_at.replace(tzinfo=timezone.utc)<datetime.now(timezone.utc):return None
 return s.user_id
@bp.post('')
@require_auth
def upload(u):
 f=request.files.get('file');e=ext(f.filename) if f else ''
 if not f or not f.filename or e not in ALLOWED:return jsonify(error='Format file tidak didukung'),400
 head=f.stream.read(128);f.stream.seek(0)
 if e=='pdf':
  if b'%PDF-' not in head:
   return jsonify(error='File PDF tidak valid'),400
 if e in {'jpg','jpeg','png','webp'}:
  try:
   from PIL import Image
   Image.open(f.stream).verify();f.stream.seek(0)
  except Exception:return jsonify(error='File gambar tidak valid'),400
 name=f'{u.id}_{uuid4().hex}.{e}';f.save(Path(current_app.config['UPLOAD_FOLDER'])/name)
 return jsonify(file_name=f.filename,file_path='/api/files/'+name),201
@bp.get('/<path:name>')
def get(name):
 uid=_request_user_id()
 if uid is None:return jsonify(error='Tidak diizinkan'),401
 owner=owner_id_from_filename(name)
 if owner is None or owner!=uid:return jsonify(error='Tidak diizinkan'),403
 return send_from_directory(current_app.config['UPLOAD_FOLDER'],name,as_attachment=False)
