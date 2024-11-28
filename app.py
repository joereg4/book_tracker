from flask import Flask, render_template, request
from routes.books import bp as books_bp
from routes.stats import bp as stats_bp
from routes.shelf import bp as shelf_bp
from models import Book
from helper import SessionLocal
import os

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your_secret_key')

# Register blueprints
app.register_blueprint(books_bp)
app.register_blueprint(stats_bp)
app.register_blueprint(shelf_bp)

# Add max and min functions to Jinja environment
app.jinja_env.globals.update(max=max, min=min)

@app.route('/')
def index():
    """Show dashboard view"""
    db = SessionLocal()
    try:
        to_read = db.query(Book).filter_by(status='to_read')\
                   .order_by(Book.created_at.desc()).all()
        reading = db.query(Book).filter_by(status='reading')\
                   .order_by(Book.created_at.desc()).all()
        read = db.query(Book).filter_by(status='read')\
                .order_by(Book.date_read.desc().nulls_last()).all()
        
        return render_template('home.html', 
                             to_read=to_read,
                             reading=reading,
                             read=read)
    finally:
        db.close()

if __name__ == '__main__':
    app.run(debug=True)