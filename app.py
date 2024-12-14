from flask import Flask
from routes.books import bp as books_bp
from routes.stats import bp as stats_bp
from routes.shelf import bp as shelf_bp
from routes.main import bp as main_bp
from routes.auth import bp as auth_bp 
from routes.profile import bp as profile_bp
from flask_login import LoginManager
from models import User
from helper import create_session, init_db
from flask_migrate import Migrate
import os
from datetime import timedelta
from flask_login import login_user

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your_secret_key')

# Configure session handling
app.config['SESSION_TYPE'] = 'filesystem'
app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=30)

# Initialize database and migrations
engine = init_db(app)

# Register blueprints
app.register_blueprint(main_bp)
app.register_blueprint(books_bp)
app.register_blueprint(stats_bp)
app.register_blueprint(shelf_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(profile_bp)

# Add max and min functions to Jinja environment
app.jinja_env.globals.update(max=max, min=min)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    db = create_session()
    try:
        return db.get(User, int(user_id))
    finally:
        db.close()

if __name__ == '__main__':
    app.run(debug=True)