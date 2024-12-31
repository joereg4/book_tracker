from flask import Flask, jsonify, abort, flash, redirect, url_for
from datetime import datetime, timezone
from extensions import (
    db, login_manager, csrf, limiter,
    mail, migrate
)
import os
import importlib
import click

def create_app(config_object=None):
    # Create Flask app with explicit instance path
    instance_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'instance')
    app = Flask(__name__, instance_path=instance_path)
    
    # Ensure instance folder exists
    if not os.path.exists(instance_path):
        os.makedirs(instance_path)

    # Configure the app - TESTING flag takes precedence to protect production DB
    if app.testing or (config_object and hasattr(config_object, 'TESTING') and config_object.TESTING):
        app.config.update({
            'TESTING': True,
            'WTF_CSRF_ENABLED': True,
            'RATELIMIT_ENABLED': False,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
            'ENV': 'testing'
        })
    elif isinstance(config_object, str):
        # Load config from string (e.g., 'config.TestConfig')
        module_name, class_name = config_object.rsplit('.', 1)
        module = importlib.import_module(module_name)
        config_class = getattr(module, class_name)
        app.config.from_object(config_class)
    elif config_object:
        app.config.from_object(config_object)
    else:
        app.config.from_object('config.Config')

    # SAFETY CHECK: If we're running tests but somehow not using in-memory database, abort
    if os.environ.get('PYTEST_CURRENT_TEST') and app.config['SQLALCHEMY_DATABASE_URI'] != 'sqlite:///:memory:':
        abort(500, "SAFETY VIOLATION: Attempting to run tests with production database!")

    # Initialize extensions
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    csrf.init_app(app)
    limiter.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)

    # Import models after extensions are initialized
    from models import User

    @login_manager.user_loader
    def load_user(user_id):
        user = db.session.get(User, int(user_id))
        if user:
            user.last_seen = datetime.now(timezone.utc)
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

    # Import and register blueprints
    from routes.auth import bp as auth_bp
    from routes.books import bp as books_bp
    from routes.main import bp as main_bp
    from routes.profile import bp as profile_bp
    from routes.shelf import bp as shelf_bp
    from routes.stats import bp as stats_bp
    from routes.monitoring import bp as monitoring_bp
    from routes.admin import bp as admin_bp
    from routes.oauth import bp as oauth_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(books_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(shelf_bp)
    app.register_blueprint(stats_bp)
    app.register_blueprint(monitoring_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(oauth_bp)

    # Error handlers
    @app.errorhandler(429)
    def ratelimit_handler(e):
        return "Rate limit exceeded. Please try again later.", 429

    # CSRF error handler
    @app.errorhandler(400)
    def handle_csrf_error(e):
        error_msg = str(e)
        if 'The CSRF session token has expired.' in error_msg or 'The CSRF session token is missing.' in error_msg:
            flash('Your session has expired. Please log in again to continue.', 'warning')
            return redirect(url_for('auth.login'))
        return e

    # Initialize CLI commands
    from cli.email_commands import init_app as init_email_cli
    from cli.user_commands import init_app as init_user_cli
    
    init_email_cli(app)
    init_user_cli(app)

    return app

# Only create the app if not being imported for testing
app = create_app() if not os.environ.get('PYTEST_CURRENT_TEST') else None

if __name__ == '__main__':
    # Run the app in debug mode if running directly
    app.run(debug=True)