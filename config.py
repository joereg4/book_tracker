import os
from datetime import timedelta
from dotenv import find_dotenv, load_dotenv

# Load environment variables
env_path = find_dotenv()
load_dotenv(env_path, override=True)

class Config:
    # Basic Flask config
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("No FLASK_SECRET_KEY set in environment")
    
    # Database config
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    if not SQLALCHEMY_DATABASE_URI:
        raise ValueError("No DATABASE_URL set in environment")
    
    # Email config with support for both Gmail OAuth2 and Postfix
    MAIL_SERVER = '127.0.0.1'  # Use IP instead of localhost
    MAIL_PORT = 1026  # MailHog SMTP port
    MAIL_USE_TLS = False
    MAIL_USERNAME = None
    MAIL_PASSWORD = None
    MAIL_USE_SSL = False
    MAIL_DEFAULT_SENDER = 'test@example.com'  # Use simple email address
    MAIL_SUPPRESS_SEND = False
    MAIL_USE_OAUTH2 = False
    
    # Rate limiting
    RATELIMIT_STORAGE_URI = os.environ.get('REDIS_URL', 'redis://localhost:6379')
    RATELIMIT_STORAGE_OPTIONS = {"decode_responses": True}
    RATELIMIT_KEY_PREFIX = 'rate_limit'
    
    # Session config
    PERMANENT_SESSION_LIFETIME = timedelta(days=31)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = os.environ.get('FLASK_ENV') == 'production'

class TestConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    RATELIMIT_ENABLED = True
    RATELIMIT_STORAGE_URI = 'memory://'
    RATELIMIT_STORAGE_OPTIONS = {"decode_responses": True}
    SERVER_NAME = 'localhost.localdomain'
    SESSION_COOKIE_SECURE = False
    MAIL_SUPPRESS_SEND = True  # Suppress actual email sending during tests
    SECRET_KEY = 'test-key'
    
    # Test email settings (MailHog)
    MAIL_SERVER = 'localhost'
    MAIL_PORT = 1026
    MAIL_USE_TLS = False
    MAIL_USERNAME = None
    MAIL_PASSWORD = None
    MAIL_DEFAULT_SENDER = 'noreply@dev-mail.readkeeper.com'
    
    def __init__(self):
        # Override the environment variable checks for tests
        pass
