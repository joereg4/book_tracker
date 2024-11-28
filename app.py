from flask import Flask
from routes.books import bp as books_bp
from routes.stats import bp as stats_bp
from routes.shelf import bp as shelf_bp
from routes.main import bp as main_bp
import os

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your_secret_key')

# Register blueprints
app.register_blueprint(main_bp)
app.register_blueprint(books_bp)
app.register_blueprint(stats_bp)
app.register_blueprint(shelf_bp)

# Add max and min functions to Jinja environment
app.jinja_env.globals.update(max=max, min=min)

if __name__ == '__main__':
    app.run(debug=True)