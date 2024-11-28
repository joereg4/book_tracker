from flask import Flask, render_template, request, redirect, url_for, flash
from olclient import OpenLibrary
from sqlalchemy import create_engine, func, desc, extract
from sqlalchemy.orm import sessionmaker
from models import Base, Book
import os
import requests
import json
from dotenv import load_dotenv
from googleapiclient.discovery import build
from datetime import datetime
import re
#from routes.main import bp as main_bp
from routes.books import bp as books_bp
from routes.stats import bp as stats_bp

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your_secret_key')

# Register blueprints
#app.register_blueprint(main_bp)
app.register_blueprint(books_bp)
app.register_blueprint(stats_bp)

# Add max and min functions to Jinja environment
app.jinja_env.globals.update(max=max, min=min)

# Database setup
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///books.db')
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)

# Load environment variables
load_dotenv()
GOOGLE_BOOKS_API_KEY = os.getenv('GOOGLE_BOOKS_API_KEY')

def strip_html_tags(text):
    """Remove HTML tags and decode HTML entities from a string"""
    if not text:
        return ''
    
    # First pass: remove bold tags specifically (replace with their content)
    text = re.sub(r'<b>(.*?)</b>', r'\1', text)
    text = re.sub(r'<strong>(.*?)</strong>', r'\1', text)
    
    # Second pass: remove remaining HTML tags
    clean = re.compile('<.*?>')
    text = re.sub(clean, ' ', text)
    
    # Replace common HTML entities
    text = text.replace('&nbsp;', ' ')\
               .replace('&amp;', '&')\
               .replace('&lt;', '<')\
               .replace('&gt;', '>')\
               .replace('&quot;', '"')\
               .replace('&#39;', "'")\
               .replace('&ndash;', '–')\
               .replace('&mdash;', '—')
    
    # Clean up extra whitespace
    text = ' '.join(text.split())
    
    return text.strip()

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

@app.route('/shelf/<shelf>')
def shelf_view(shelf):
    """Display books on a specific shelf"""
    titles = {
        'to_read': 'To Read',
        'reading': 'Currently Reading',
        'read': 'Read'
    }
    
    db = SessionLocal()
    try:
        # Get search query
        search_query = request.args.get('search', '').strip()
        
        # Base query
        query = db.query(Book).filter_by(status=shelf)
        
        # Apply search if provided
        if search_query:
            search_filter = (
                (Book.title.ilike(f'%{search_query}%')) |
                (Book.authors.ilike(f'%{search_query}%')) |
                (Book.description.ilike(f'%{search_query}%')) |
                (Book.publisher.ilike(f'%{search_query}%')) |
                (Book.categories.ilike(f'%{search_query}%'))
            )
            query = query.filter(search_filter)
        
        # Apply ordering
        if shelf == 'read':
            query = query.order_by(Book.date_read.desc().nulls_last(),
                                 Book.created_at.desc())
        else:
            query = query.order_by(Book.created_at.desc())
            
        books = query.all()
            
        return render_template('view.html',
                             books=books,
                             title=titles.get(shelf, 'Books'),
                             current_shelf=shelf)
    finally:
        db.close()

if __name__ == '__main__':
    app.run(debug=True)