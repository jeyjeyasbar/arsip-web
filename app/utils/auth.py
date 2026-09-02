from functools import wraps
from datetime import datetime, timedelta, timezone
import hashlib, secrets, jwt
from flask import request, jsonify, current_app
from app.models import db, User, RefreshSession

def _hash(v): return hashlib.sha256(v.encode()).hexdigest()

def make_access_token(user):
    now=datetime.now(timezone.utc)
    return jwt.encode({'sub':str(user.id),'ver':user.token_version,'type':'access','iat':now,'exp':now+timedelta(minutes=current_app.config['ACCESS_TOKEN_MINUTES'])}, current_app.config['SECRET_KEY'], algorithm='HS256')

def make_refresh_token(user):
    raw=secrets.token_urlsafe(48); now=datetime.now(timezone.utc); exp=now+timedelta(days=current_app.config['REFRESH_TOKEN_DAYS'])
    db.session.add(RefreshSession(user_id=user.id,token_hash=_hash(raw),expires_at=exp)); db.session.commit(); return raw

def require_auth(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        raw=request.headers.get('Authorization','')
        if not raw.startswith('Bearer '): return jsonify(error='Token tidak ditemukan'),401
        try:
            payload=jwt.decode(raw[7:],current_app.config['SECRET_KEY'],algorithms=['HS256'])
            if payload.get('type')!='access': raise ValueError()
            uid=int(payload['sub'])
        except Exception: return jsonify(error='Token tidak valid atau kedaluwarsa'),401
        user=db.session.get(User,uid)
        if not user or payload.get('ver')!=user.token_version: return jsonify(error='Sesi tidak berlaku'),401
        return fn(user,*args,**kwargs)
    return wrapper
