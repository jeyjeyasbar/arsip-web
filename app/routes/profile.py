from flask import Blueprint,request,jsonify,current_app
from pathlib import Path
from uuid import uuid4
from app.models import db,User
from app.utils.auth import require_auth
from app.utils.serializers import user_public
from app.utils.storage import remove_file
bp=Blueprint('profile',__name__)
@bp.get('')
@require_auth
def get(u):return jsonify(user=user_public(u))
@bp.put('')
@require_auth
def update(u):
 d=request.get_json(silent=True) or {}
 for a,b in [('name','name'),('campus','campus'),('faculty','faculty'),('program','program')]:
  if a in d:setattr(u,b,str(d[a]).strip())
 db.session.commit();return jsonify(user=user_public(u))
@bp.put('/email')
@require_auth
def email(u):
 import re
 v=str((request.get_json(silent=True) or {}).get('email','')).strip().lower()
 if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$',v):return jsonify(error='Email tidak valid'),400
 if User.query.filter(User.email==v,User.id!=u.id).first():return jsonify(error='Email sudah digunakan'),409
 u.email=v;db.session.commit();return jsonify(user=user_public(u))
@bp.post('/photo')
@require_auth
def photo(u):
 f=request.files.get('file');e=(f.filename.rsplit('.',1)[-1].lower() if f and '.' in f.filename else '')
 if not f or e not in {'jpg','jpeg','png','webp'}:return jsonify(error='Foto JPG, PNG, atau WEBP wajib dipilih'),400
 try:
  from PIL import Image
  Image.open(f.stream).verify();f.stream.seek(0)
 except Exception:return jsonify(error='File gambar tidak valid'),400
 old_photo=u.photo
 name=f'profile_{u.id}_{uuid4().hex}.{e}';f.save(Path(current_app.config['UPLOAD_FOLDER'])/name);u.photo='/api/files/'+name;db.session.commit()
 remove_file(old_photo)
 return jsonify(user=user_public(u))
