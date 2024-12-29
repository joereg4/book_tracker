import os
from datetime import timedelta

class Config:
    # Basic Flask config
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY') or 'dev-key-please-change'
    
    # Database config
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://localhost/books'  # PostgreSQL is required for production
    if not SQLALCHEMY_DATABASE_URI.startswith('postgresql://'):
        raise ValueError('Production database must be PostgreSQL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Email config with SendGrid support
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.sendgrid.net')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'apikey'  # This is always 'apikey' for SendGrid
    MAIL_PASSWORD = os.environ.get('SENDGRID_API_KEY')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@example.com')
    MAIL_SUPPRESS_SEND = os.environ.get('FLASK_ENV') != 'production'
    
    # Rate limiting
    RATELIMIT_STORAGE_URI = os.environ.get('REDIS_URL', 'redis://localhost:6379')
    RATELIMIT_STORAGE_OPTIONS = {"decode_responses": True}
    RATELIMIT_KEY_PREFIX = 'rate_limit'
    
    # Session config
    PERMANENT_SESSION_LIFETIME = timedelta(days=31)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Only require secure cookies in production
    SESSION_COOKIE_SECURE = os.environ.get('FLASK_ENV') == 'production'

class TestConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # Use SQLite for faster tests
    RATELIMIT_ENABLED = True
    RATELIMIT_STORAGE_URI = 'memory://'  # Use in-memory storage for tests
    RATELIMIT_STORAGE_OPTIONS = {"decode_responses": True}  # Consistent decode option
    SERVER_NAME = 'localhost.localdomain'
    SESSION_COOKIE_SECURE = False  # Allow testing without HTTPS
    MAIL_SUPPRESS_SEND = True
    
    def __init__(self):
        # Override the PostgreSQL check for tests
        pass