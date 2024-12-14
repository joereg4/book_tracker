from flask import Flask, jsonify
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from utils.email import mail
from datetime import datetime, UTC

app = Flask(__name__)

# Use TestConfig for testing, regular Config for production
if app.config.get('TESTING'):
    app.config.from_object('config.TestConfig')
else:
    app.config.from_object('config.Config')

# Initialize extensions
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

csrf = CSRFProtect(app)

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    storage_uri="memory://",
    default_limits=None  # Remove default limits
)

# Expose limiter on app instance for testing
app.limiter = limiter

# Import and register blueprints
from routes.auth import bp as auth_bp
from routes.books import bp as books_bp
from routes.main import bp as main_bp
from routes.profile import bp as profile_bp
from routes.shelf import bp as shelf_bp
from routes.stats import bp as stats_bp

app.register_blueprint(auth_bp)
app.register_blueprint(books_bp)
app.register_blueprint(main_bp)
app.register_blueprint(profile_bp)
app.register_blueprint(shelf_bp)
app.register_blueprint(stats_bp)

# Initialize database
from models import db, User

db.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    user = db.session.get(User, int(user_id))
    if user:
        user.last_seen = datetime.now(UTC)
        db.session.commit()
    return user

# Apply rate limits to specific routes
@limiter.limit("5 per minute")
@app.route("/login-limit-check")
def login_limit():
    return jsonify({"status": "ok"})

@limiter.limit("30 per minute")
@app.route("/books/search-limit-check")
def search_limit():
    return jsonify({"status": "ok"})

mail.init_app(app)