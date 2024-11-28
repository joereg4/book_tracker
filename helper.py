from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from models import Book, Base
import re

# Configure your database URL
DATABASE_URL = 'sqlite:///books.db'  # Example using SQLite

# Create a new database session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def get_book_status(open_library_id):
    """Check if a book exists in the database and return its status."""
    db = SessionLocal()
    try:
        book = db.query(Book).filter_by(open_library_id=open_library_id).first()
        if book:
            return book.status
        return None
    finally:
        db.close()

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
    