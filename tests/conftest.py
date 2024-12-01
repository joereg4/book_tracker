import pytest
import os
import sys
import tempfile
from sqlalchemy import create_engine, text

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from models import Base

@pytest.fixture(scope='session', autouse=True)
def database():
    """Create a temporary test database"""
    # Create temporary database file
    db_fd, db_path = tempfile.mkstemp()
    database_url = f'sqlite:///{db_path}'
    
    # Force test database URL in environment BEFORE any imports
    os.environ['TEST_DATABASE_URL'] = database_url
    os.environ['TESTING'] = 'True'
    
    # Create tables
    engine = create_engine(database_url)
    Base.metadata.create_all(engine)
    
    # Create FTS table and triggers
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE VIRTUAL TABLE IF NOT EXISTS books_fts USING fts5(
                title, 
                authors, 
                description, 
                categories,
                publisher,
                content='books',
                content_rowid='id',
                tokenize='porter'
            );
        """))
        
        # Create triggers
        conn.execute(text("""
            CREATE TRIGGER IF NOT EXISTS books_ai AFTER INSERT ON books BEGIN
                INSERT INTO books_fts(rowid, title, authors, description, categories, publisher)
                VALUES (new.id, new.title, new.authors, new.description, new.categories, new.publisher);
            END;
        """))
        
        conn.execute(text("""
            CREATE TRIGGER IF NOT EXISTS books_au AFTER UPDATE ON books BEGIN
                UPDATE books_fts SET
                    title = new.title,
                    authors = new.authors,
                    description = new.description,
                    categories = new.categories,
                    publisher = new.publisher
                WHERE rowid = old.id;
            END;
        """))
        
        conn.execute(text("""
            CREATE TRIGGER IF NOT EXISTS books_ad AFTER DELETE ON books BEGIN
                DELETE FROM books_fts WHERE rowid = old.id;
            END;
        """))
        
        conn.commit()
    
    yield database_url
    
    # Cleanup
    os.close(db_fd)
    os.unlink(db_path)
    
    # Remove test environment variables
    del os.environ['TEST_DATABASE_URL']
    del os.environ['TESTING']

@pytest.fixture(scope='session')
def app(database):
    """Create test application"""
    from app import app
    app.config.update({
        'TESTING': True,
        'DATABASE_URL': database,
        'SERVER_NAME': 'test.local'
    })
    return app

@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()

@pytest.fixture
def db_session(database):
    """Create test database session"""
    from helper import get_db
    session = next(get_db())
    try:
        yield session
        # Clear all tables after each test
        for table in reversed(Base.metadata.sorted_tables):
            session.execute(table.delete())
        session.commit()
    finally:
        session.rollback()
        session.close() 