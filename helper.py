from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from models import Book, Base
import re
import os

def get_database_url():
    """Get database URL based on environment"""
    if os.getenv('TESTING') == 'True':
        return os.getenv('TEST_DATABASE_URL')
    return os.getenv('DATABASE_URL', 'sqlite:///books.db')

# Create engine and session factory based on environment
def create_session():
    engine = create_engine(get_database_url())
    return sessionmaker(bind=engine)()

def get_db():
    """Database dependency"""
    db = create_session()
    try:
        yield db
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
    