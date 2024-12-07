from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from flask_migrate import Migrate
import re
import os

def get_database_url():
    """Get database URL based on environment"""
    # First check for explicit test database URL
    if 'TEST_DATABASE_URL' in os.environ:
        return os.environ['TEST_DATABASE_URL']
        
    # For production, always use the books.db in the project root
    current_file = os.path.abspath(__file__)  # Gets the helper.py path
    project_root = os.path.dirname(current_file)  # Get the directory containing helper.py
    default_db_path = os.path.join(project_root, 'books.db')
    
    return os.environ.get('DATABASE_URL', f'sqlite:///{default_db_path}')

migrate = None
_engine = None  # Add this for singleton pattern

def get_engine():
    """Get or create SQLAlchemy engine"""
    global _engine
    if _engine is None:
        _engine = create_engine(get_database_url())
    return _engine

def init_db(app):
    """Initialize database and migrations"""
    global migrate
    from models import Base
    engine = get_engine()
    migrate = Migrate(app, Base.metadata)
    return engine

# Create engine and session factory based on environment
def create_session():
    engine = get_engine()
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

def reset_engine():
    """Reset the database engine (useful for testing)"""
    global _engine
    if _engine is not None:
        _engine.dispose()
    _engine = None
    