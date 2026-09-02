from flask import Blueprint,request,jsonify
from app.models import db,Payment,Activity,Account,Document
from app.utils.auth import require_auth
from app.utils.serializers import record_public,account_public
from app.utils.crypto import encrypt
from app.utils.storage import remove_file
bp=Blueprint('records',__name__)
# tuple kelima = nama field yang menyimpan path file upload (untuk kind ini), atau None jika tidak ada
MAP={'payments':(Payment,['category','date','semester','description','amount','file_path','file_name'],['category','date'],'file_path'),'activities':(Activity,['name','date','description','photo_path','photo_name'],['name','date'],'photo_path'),'accounts':(Account,['service','username','password','description'],['service','username'],None),'documents':(Document,['name','category','date','description','file_path','file_name'],['name','category','date'],'file_path')}
def public(x):return account_public(x) if isinstance(x,Account) else record_public(x)
def to_amount(v):
 try:return int(v)
 except (TypeError,ValueError):return 0
for kind,(Model,fields,required,file_field) in MAP.items():
 def listing(u,Model=Model): return jsonify(items=[public(x) for x in Model.query.filter_by(user_id=u.id).order_by(Model.id.desc()).all()])
 listing=bp.route('/'+kind,methods=['GET'],endpoint=kind+'_list')(require_auth(listing))
 def create(u,Model=Model,fields=fields,required=required):
  d=request.get_json(silent=True) or {}
  if any(not str(d.get(k,'')).strip() for k in required):return jsonify(error='Field wajib belum diisi',fields=required),400
  x=Model(user_id=u.id)
  for f in fields:
   if f=='password':x.password_enc=encrypt(str(d.get(f,'')))
   elif f=='amount':
    if f in d:x.amount=to_amount(d[f])
   elif f in d:setattr(x,f,d[f])
  db.session.add(x);db.session.commit();return jsonify(item=public(x)),201
 bp.add_url_rule('/'+kind,view_func=require_auth(create),methods=['POST'],endpoint=kind+'_create')
 def update(u,item_id,Model=Model,fields=fields,file_field=file_field):
  x=Model.query.filter_by(id=item_id,user_id=u.id).first()
  if not x:return jsonify(error='Data tidak ditemukan'),404
  d=request.get_json(silent=True) or {}
  old_file=getattr(x,file_field,None) if file_field else None
  for f in fields:
   if f=='password' and f in d:x.password_enc=encrypt(str(d[f]))
   elif f=='amount':
    if f in d:x.amount=to_amount(d[f])
   elif f in d:setattr(x,f,d[f])
  db.session.commit()
  # jika file diganti dengan yang baru, hapus file lama dari disk agar tidak jadi sampah/orphan
  if file_field and file_field in d:
   new_file=getattr(x,file_field,None)
   if old_file and old_file!=new_file:remove_file(old_file)
  return jsonify(item=public(x))
 bp.add_url_rule('/'+kind+'/<int:item_id>',view_func=require_auth(update),methods=['PUT'],endpoint=kind+'_update')
 def delete(u,item_id,Model=Model,file_field=file_field):
  x=Model.query.filter_by(id=item_id,user_id=u.id).first()
  if not x:return jsonify(error='Data tidak ditemukan'),404
  old_file=getattr(x,file_field,None) if file_field else None
  db.session.delete(x);db.session.commit()
  remove_file(old_file)
  return jsonify(message='Data dihapus')
 bp.add_url_rule('/'+kind+'/<int:item_id>',view_func=require_auth(delete),methods=['DELETE'],endpoint=kind+'_delete')
