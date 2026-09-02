from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def now(): return datetime.now(timezone.utc)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    campus = db.Column(db.String(160), default='')
    faculty = db.Column(db.String(160), default='')
    program = db.Column(db.String(160), default='')
    photo = db.Column(db.String(255))
    token_version = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime(timezone=True), default=now)
    updated_at = db.Column(db.DateTime(timezone=True), default=now, onupdate=now)

class RefreshSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False, index=True)
    token_hash = db.Column(db.String(64), unique=True, nullable=False, index=True)
    expires_at = db.Column(db.DateTime(timezone=True), nullable=False)
    revoked_at = db.Column(db.DateTime(timezone=True))
    created_at = db.Column(db.DateTime(timezone=True), default=now)

class Payment(db.Model):
    id=db.Column(db.Integer,primary_key=True); user_id=db.Column(db.Integer,db.ForeignKey('user.id',ondelete='CASCADE'),nullable=False,index=True)
    category=db.Column(db.String(100),nullable=False); date=db.Column(db.String(20),nullable=False); semester=db.Column(db.String(80),default=''); description=db.Column(db.Text,default=''); amount=db.Column(db.Integer,default=0); file_path=db.Column(db.String(255)); file_name=db.Column(db.String(255)); created_at=db.Column(db.DateTime(timezone=True),default=now)
class Activity(db.Model):
    id=db.Column(db.Integer,primary_key=True); user_id=db.Column(db.Integer,db.ForeignKey('user.id',ondelete='CASCADE'),nullable=False,index=True)
    name=db.Column(db.String(160),nullable=False); date=db.Column(db.String(20),nullable=False); description=db.Column(db.Text,default=''); photo_path=db.Column(db.String(255)); photo_name=db.Column(db.String(255)); created_at=db.Column(db.DateTime(timezone=True),default=now)
class Account(db.Model):
    id=db.Column(db.Integer,primary_key=True); user_id=db.Column(db.Integer,db.ForeignKey('user.id',ondelete='CASCADE'),nullable=False,index=True)
    service=db.Column(db.String(120),nullable=False); username=db.Column(db.String(255),nullable=False); password_enc=db.Column(db.Text,default=''); description=db.Column(db.Text,default=''); created_at=db.Column(db.DateTime(timezone=True),default=now)
class Document(db.Model):
    id=db.Column(db.Integer,primary_key=True); user_id=db.Column(db.Integer,db.ForeignKey('user.id',ondelete='CASCADE'),nullable=False,index=True)
    name=db.Column(db.String(200),nullable=False); category=db.Column(db.String(100),nullable=False); date=db.Column(db.String(20),nullable=False); description=db.Column(db.Text,default=''); file_path=db.Column(db.String(255)); file_name=db.Column(db.String(255)); created_at=db.Column(db.DateTime(timezone=True),default=now)
class PasswordReset(db.Model):
    id=db.Column(db.Integer,primary_key=True); user_id=db.Column(db.Integer,db.ForeignKey('user.id',ondelete='CASCADE'),nullable=False,index=True)
    token_hash=db.Column(db.String(64),unique=True,nullable=False,index=True); expires_at=db.Column(db.DateTime(timezone=True),nullable=False); used_at=db.Column(db.DateTime(timezone=True)); created_at=db.Column(db.DateTime(timezone=True),default=now)
class EmailVerification(db.Model):
    id=db.Column(db.Integer,primary_key=True); user_id=db.Column(db.Integer,db.ForeignKey('user.id',ondelete='CASCADE'),nullable=False,index=True)
    token_hash=db.Column(db.String(64),unique=True,nullable=False,index=True); expires_at=db.Column(db.DateTime(timezone=True),nullable=False); used_at=db.Column(db.DateTime(timezone=True)); created_at=db.Column(db.DateTime(timezone=True),default=now)
