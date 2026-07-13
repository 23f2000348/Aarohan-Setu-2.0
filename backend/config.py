import os

class Config:
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    
    if os.environ.get('TESTING') == 'True':
        SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    else:
        SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'aarohan_setu.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    
    SECRET_KEY = os.environ.get('SECRET_KEY', 'aarohan_setu_secret_key_2026_!')
    
    
    CACHE_TYPE = 'RedisCache'
    CACHE_REDIS_HOST = 'localhost'
    CACHE_REDIS_PORT = 6379
    CACHE_REDIS_DB = 0
    CACHE_DEFAULT_TIMEOUT = 300  
    
    
    CELERY_BROKER_URL = 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
    
    
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  
    
    
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}

    @staticmethod
    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS
