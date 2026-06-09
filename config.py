import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'acooda-secret-key-2024-adhiyamaan')
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'mysql+pymysql://root:1234@localhost/ACOODA'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Mail
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', 'yathishanbu@gmail.com')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', 'ujbywhrwxctovmwc')
    MAIL_DEFAULT_SENDER = ('ACOODA - ACE', os.environ.get('MAIL_USERNAME', 'yathishanbu@gmail.com'))
    
    # File Upload
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'doc', 'docx'}
    
    # Session
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
    
    # WTF CSRF
    WTF_CSRF_ENABLED = True
