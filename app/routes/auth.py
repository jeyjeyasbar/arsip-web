import hashlib,secrets,re
from datetime import datetime,timedelta,timezone
from flask import Blueprint,request,jsonify,current_app,make_response
from werkzeug.security import generate_password_hash,check_password_hash
from app.models import db,User,PasswordReset,RefreshSession,EmailVerification
from app.utils.auth import make_access_token,make_refresh_token,require_auth
from app.utils.serializers import user_public
from app.utils.emailer import send_reset_email
bp=Blueprint('auth',__name__)

def valid_email(v): return bool(re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$',v or ''))
def rh(v): return hashlib.sha256(v.encode()).hexdigest()
def issue(user):
    raw=make_refresh_token(user); r=make_response(jsonify(user=user_public(user),access_token=make_access_token(user)))
    # path='/api' (bukan hanya '/api/auth') agar cookie yang sama juga terkirim otomatis
    # ke /api/files/... sehingga endpoint download bisa memverifikasi pemilik file (lihat files.py)
    r.set_cookie('refresh_token',raw,httponly=True,secure=current_app.config['COOKIE_SECURE'],samesite='Lax',max_age=current_app.config['REFRESH_TOKEN_DAYS']*86400,path='/api')
    return r
def revoke_all_sessions(user_id):
    RefreshSession.query.filter_by(user_id=user_id,revoked_at=None).update({'revoked_at':datetime.now(timezone.utc)})
@bp.post('/register')
def register():
 d=request.get_json(silent=True) or {}; name=str(d.get('name','')).strip(); email=str(d.get('email','')).strip().lower(); pw=str(d.get('password',''))
 if not name or not valid_email(email) or len(pw)<8:return jsonify(error='Nama, email valid, dan kata sandi minimal 8 karakter wajib diisi'),400
 if User.query.filter_by(email=email).first():return jsonify(error='Email sudah terdaftar'),409
 u=User(name=name,email=email,password_hash=generate_password_hash(pw));db.session.add(u);db.session.commit()
 raw=secrets.token_urlsafe(32)
 db.session.add(EmailVerification(user_id=u.id,token_hash=rh(raw),expires_at=datetime.now(timezone.utc)+timedelta(days=1)))
 db.session.commit()
 link=current_app.config['FRONTEND_URL'].rstrip('/')+'/?verify_email='+raw
 if current_app.config['ENVIRONMENT']!='production':
    return jsonify(user=user_public(u),access_token=make_access_token(u),dev_verify_token=raw,dev_verify_link=link)
 return jsonify(user=user_public(u),message='Registrasi berhasil. Silakan cek email untuk verifikasi akun.')
@bp.post('/login')
def login():
 d=request.get_json(silent=True) or {}; email=str(d.get('email','')).strip().lower();pw=str(d.get('password',''));u=User.query.filter_by(email=email).first()
 if not u or not check_password_hash(u.password_hash,pw):return jsonify(error='Email atau kata sandi salah'),401
 ev=EmailVerification.query.filter_by(user_id=u.id,used_at=None).order_by(EmailVerification.id.desc()).first()
 if ev and ev.expires_at.replace(tzinfo=timezone.utc)>=datetime.now(timezone.utc):
    return jsonify(error='Email belum diverifikasi'),403
 if ev is None:
    # Old data / legacy user: allow login if no verification record exists.
    pass
 return issue(u)
@bp.post('/verify-email')
def verify_email():
 d=request.get_json(silent=True) or {}; token=str(d.get('token',''))
 v=EmailVerification.query.filter_by(token_hash=rh(token),used_at=None).first()
 if not v or v.expires_at.replace(tzinfo=timezone.utc)<datetime.now(timezone.utc):
    return jsonify(error='Token verifikasi email tidak valid atau kedaluwarsa'),400
 v.used_at=datetime.now(timezone.utc)
 db.session.commit()
 return jsonify(message='Email berhasil diverifikasi')
@bp.post('/refresh')
def refresh():
 raw=request.cookies.get('refresh_token','');s=RefreshSession.query.filter_by(token_hash=rh(raw),revoked_at=None).first()
 if not s or s.expires_at.replace(tzinfo=timezone.utc)<datetime.now(timezone.utc):return jsonify(error='Refresh token tidak valid'),401
 u=db.session.get(User,s.user_id);s.revoked_at=datetime.now(timezone.utc);db.session.commit();return issue(u)
@bp.post('/logout')
def logout():
 raw=request.cookies.get('refresh_token','');s=RefreshSession.query.filter_by(token_hash=rh(raw),revoked_at=None).first()
 if s:s.revoked_at=datetime.now(timezone.utc);db.session.commit()
 r=make_response(jsonify(message='Berhasil keluar'));r.delete_cookie('refresh_token',path='/api');return r
@bp.get('/me')
@require_auth
def me(u):return jsonify(user=user_public(u))
@bp.post('/forgot-password')
def forgot():
 d=request.get_json(silent=True) or {};email=str(d.get('email','')).strip().lower();u=User.query.filter_by(email=email).first();out={'message':'Jika email terdaftar, instruksi reset kata sandi telah dikirim.'}
 if not u or not valid_email(email):return jsonify(**out)
 PasswordReset.query.filter_by(user_id=u.id,used_at=None).update({'used_at':datetime.now(timezone.utc)})
 raw=secrets.token_urlsafe(48);db.session.add(PasswordReset(user_id=u.id,token_hash=rh(raw),expires_at=datetime.now(timezone.utc)+timedelta(minutes=30)));db.session.commit();link=current_app.config['FRONTEND_URL'].rstrip('/')+'/?reset_token='+raw
 try:sent=send_reset_email(u.email,u.name,link)
 except Exception:current_app.logger.exception('reset mail failed');sent=False
 if not sent and current_app.config['ENVIRONMENT']!='production':out['dev_reset_token']=raw
 return jsonify(**out)
@bp.post('/reset-password')
def reset():
 d=request.get_json(silent=True) or {};token=str(d.get('token',''));pw=str(d.get('password',''));r=PasswordReset.query.filter_by(token_hash=rh(token),used_at=None).first()
 if len(pw)<8:return jsonify(error='Kata sandi minimal 8 karakter'),400
 if not r or r.expires_at.replace(tzinfo=timezone.utc)<datetime.now(timezone.utc):return jsonify(error='Token reset tidak valid atau kedaluwarsa'),400
 u=db.session.get(User,r.user_id);u.password_hash=generate_password_hash(pw);u.token_version+=1;r.used_at=datetime.now(timezone.utc);revoke_all_sessions(u.id);db.session.commit();return jsonify(message='Kata sandi berhasil diubah')
@bp.put('/password')
@require_auth
def change(u):
 d=request.get_json(silent=True) or {};old=str(d.get('current_password',''));new=str(d.get('new_password',''))
 if not check_password_hash(u.password_hash,old):return jsonify(error='Kata sandi lama salah'),400
 if len(new)<8:return jsonify(error='Kata sandi baru minimal 8 karakter'),400
 u.password_hash=generate_password_hash(new);u.token_version+=1;revoke_all_sessions(u.id);db.session.commit()
 # keluarkan sesi refresh baru untuk perangkat ini; semua sesi refresh lama (perangkat lain / dicuri) sudah dicabut di atas
 return issue(u)
