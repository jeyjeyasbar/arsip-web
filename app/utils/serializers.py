def user_public(u):
    return {'id':u.id,'name':u.name,'email':u.email,'campus':u.campus or '','faculty':u.faculty or '','program':u.program or '','photo':u.photo}

def record_public(x):
    base={'id':x.id,'created_at':x.created_at.isoformat() if x.created_at else None}
    if x.__class__.__name__=='Payment': base.update(category=x.category,date=x.date,semester=x.semester or '',description=x.description or '',amount=x.amount or 0,file_path=x.file_path,file_name=x.file_name)
    elif x.__class__.__name__=='Activity': base.update(name=x.name,date=x.date,description=x.description or '',photo_path=x.photo_path,photo_name=x.photo_name)
    elif x.__class__.__name__=='Document': base.update(name=x.name,category=x.category,date=x.date,description=x.description or '',file_path=x.file_path,file_name=x.file_name)
    return base

def account_public(x):
    from app.utils.crypto import decrypt
    return {'id':x.id,'service':x.service,'username':x.username,'password':decrypt(x.password_enc) if x.password_enc else '','description':x.description or '','created_at':x.created_at.isoformat() if x.created_at else None}
