from flask import Flask
from routes.books import bp as books_bp
from routes.stats import bp as stats_bp
from routes.shelf import bp as shelf_bp
from routes.main import bp as main_bp
from routes.auth import bp as auth_bp 
from flask_login import LoginManager
from models import User
from helper import create_session
import os

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your_secret_key')

# Register blueprints
app.register_blueprint(main_bp)
app.register_blueprint(books_bp)
app.register_blueprint(stats_bp)
app.register_blueprint(shelf_bp)
app.register_blueprint(auth_bp)

# Add max and min functions to Jinja environment
app.jinja_env.globals.update(max=max, min=min)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    db = create_session()
    try:
        return db.query(User).get(int(user_id))
    finally:
        db.close()

if __name__ == '__main__':
    app.run(debug=True)