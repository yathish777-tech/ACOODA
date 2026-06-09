"""
Quick-start config using SQLite (no MySQL needed for testing)
Replace config.py content with this for local development.
"""
import os
from datetime import timedelta

class Config:
    SECRET_KEY = 'acooda-secret-key-2024-adhiyamaan-ace'

    # SQLite for easy local development — no MySQL required
    SQLALCHEMY_DATABASE_URI = 'sqlite:///ACOODA'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Mail (disabled for demo — set real credentials to enable)
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', 'yathishanbu@gmail.com')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', 'ujbywhrwxctovmwc')
    MAIL_DEFAULT_SENDER = ('ACOODA - ACE', os.environ.get('MAIL_USERNAME', 'yathishanbu@gmail.com'))

    # File Upload
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'doc', 'docx'}

    # Session
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
    WTF_CSRF_ENABLED = True
