import os
from flask import Flask, send_from_directory, jsonify
from flask_login import LoginManager
from flask_caching import Cache
import redis

from backend.models.db_models import db, User, cache
from backend.routes.auth import auth_bp
from backend.routes.admin import admin_bp
from backend.routes.company import company_bp
from backend.routes.student import student_bp

def create_app():
    app = Flask(__name__, static_folder='../frontend', static_url_path='')
    
    from backend.config import Config
    app.config.from_object(Config)
    
    for folder in [
        app.config['UPLOAD_FOLDER'],
        os.path.join(app.config['BASE_DIR'], 'logs'),
        os.path.join(app.config['BASE_DIR'], 'reports'),
        os.path.normpath(os.path.join(app.config['BASE_DIR'], '..', 'frontend', 'exports'))
    ]:
        os.makedirs(folder, exist_ok=True)
    
    db.init_app(app)
    
    # Initializing Cache with automatic fallback if Redis is down
    try:
        r = redis.Redis(host=app.config['CACHE_REDIS_HOST'], 
                        port=app.config['CACHE_REDIS_PORT'], 
                        db=app.config['CACHE_REDIS_DB'], 
                        socket_timeout=1.0)
        r.ping()
        print("Successfully connected to Redis cache backend.")
    except Exception as e:
        print(f"Warning: Redis connection failed ({e}). Falling back to SimpleCache.")
        app.config['CACHE_TYPE'] = 'SimpleCache'
        
    cache.init_app(app)
    
    # Initializing  Login Manager
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
        
    @login_manager.unauthorized_handler
    def unauthorized():
        return jsonify({'message': 'Unauthorized. Please log in.'}), 401
        
    # Registering Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(company_bp)
    app.register_blueprint(student_bp)
    
    @app.route('/api/resumes/<filename>')
    def serve_resume(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
        

        
    @app.route('/exports/<filename>')
    def serve_export(filename):
        exports_dir = os.path.normpath(os.path.join(app.config['BASE_DIR'], '..', 'frontend', 'exports'))
        return send_from_directory(exports_dir, filename, as_attachment=True)
        
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_spa(path):
        if path.startswith('api/'):
            return jsonify({'message': 'API endpoint not found.'}), 404
        return send_from_directory(app.static_folder, 'index.html')
        
    with app.app_context():
        db.create_all()
        admin = User.query.filter_by(role='admin').first()
        if not admin:
            admin = User(email='admin@aarohansetu.in', role='admin')
            admin.set_password('admin_password')
            db.session.add(admin)
            db.session.commit()
            print("Programmatic database initialized and default admin account created.")
            
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5001, debug=True)