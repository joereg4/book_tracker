from flask import Flask, jsonify
from datetime import datetime, UTC
from extensions import (
    db, login_manager, csrf, limiter,
    mail, migrate
)
import os

def create_app(config_object=None):
    # Create Flask app with explicit instance path
    instance_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'instance')
    app = Flask(__name__, instance_path=instance_path)
    
    # Ensure instance folder exists
    if not os.path.exists(instance_path):
        os.makedirs(instance_path)

    # Configure the app
    if config_object:
        app.config.from_object(config_object)
    elif os.environ.get('FLASK_TESTING'):
        app.config.from_object('config.TestConfig')
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # Force in-memory database for tests
    else:
        app.config.from_object('config.Config')

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

    return app

app = create_app()

if __name__ == '__main__':
    # Run the app in debug mode if running directly
    app.run(debug=True)