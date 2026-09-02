from pathlib import Path
from flask import Flask, jsonify, render_template
from flask_cors import CORS
from .models import db
from .routes.auth import bp as auth_bp
from .routes.profile import bp as profile_bp
from .routes.records import bp as records_bp
from .routes.files import bp as files_bp

def create_app(test_config=None):
 app=Flask(__name__,instance_relative_config=True);app.config.from_object('config.Config')
 if test_config:app.config.update(test_config)
 Path(app.instance_path).mkdir(parents=True,exist_ok=True);Path(app.config['UPLOAD_FOLDER']).mkdir(parents=True,exist_ok=True)
 db.init_app(app);CORS(app,supports_credentials=True,resources={r'/api/*':{'origins':app.config['FRONTEND_URL']}})
 app.register_blueprint(auth_bp,url_prefix='/api/auth');app.register_blueprint(profile_bp,url_prefix='/api/profile');app.register_blueprint(records_bp,url_prefix='/api');app.register_blueprint(files_bp,url_prefix='/api/files')
 @app.get('/')
 def index():return render_template('index.html')
 @app.get('/api/health')
 def health():return jsonify(status='ok',service='arsip-mahasiswa')
 @app.errorhandler(413)
 def too_large(e):return jsonify(error='Ukuran file terlalu besar'),413
 with app.app_context():db.create_all()
 return app
