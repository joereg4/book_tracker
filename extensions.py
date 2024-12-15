from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_mail import Mail
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask import request
import redis

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()

def on_rate_limit_hit(limiter, hit):
    """Callback for rate limit hits"""
    from routes.monitoring import record_rate_limit_hit
    endpoint = request.endpoint
    if endpoint:
        record_rate_limit_hit(endpoint, get_remote_address())

# Try to connect to Redis, fall back to memory if not available
try:
    redis.Redis(host='localhost', port=6379).ping()
    storage_uri = "redis://localhost:6379"
except (redis.ConnectionError, redis.RedisError):
    storage_uri = "memory://"

limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=storage_uri,
    storage_options={"decode_responses": True},
    default_limits=None
)

mail = Mail()
migrate = Migrate() 