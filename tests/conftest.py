import pytest
import os
import sys
import tempfile
from sqlalchemy import create_engine, text

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from models import Base
from tests.config import get_test_db_url, cleanup_test_db

@pytest.fixture(scope='session', autouse=True)
def database():
    """Create a temporary test database"""
    # Create temporary database file in /tmp
    db_fd, db_path = tempfile.mkstemp(prefix='test_books_', suffix='.db')
    database_url = f'sqlite:///{db_path}'
    
    # Set test database URL
    os.environ['TEST_DATABASE_URL'] = database_url
    
    try:
        # Create engine and tables
        engine = create_engine(database_url)
        Base.metadata.create_all(engine)
        
        # Setup FTS
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
                    tokenize='porter unicode61 remove_diacritics 2'
                );
            """))
            
            # Update the insert trigger to handle NULL values
            conn.execute(text("""
                CREATE TRIGGER IF NOT EXISTS books_ai AFTER INSERT ON books BEGIN
                    INSERT INTO books_fts(rowid, title, authors, description, categories, publisher)
                    VALUES (
                        new.id, 
                        COALESCE(new.title, ''),
                        COALESCE(new.authors, ''),
                        COALESCE(new.description, ''),
                        COALESCE(new.categories, ''),
                        COALESCE(new.publisher, '')
                    );
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
            
            # Add debug verification
            conn.execute(text("""
                CREATE TRIGGER IF NOT EXISTS books_ai_verify AFTER INSERT ON books BEGIN
                    SELECT RAISE(ROLLBACK, 'FTS not updated')
                    WHERE NOT EXISTS (
                        SELECT 1 FROM books_fts WHERE rowid = new.id
                    );
                END;
            """))
            
            conn.commit()
        
        yield database_url
        
    finally:
        # Clean up
        if 'TEST_DATABASE_URL' in os.environ:
            del os.environ['TEST_DATABASE_URL']
        os.close(db_fd)
        os.unlink(db_path)

@pytest.fixture(scope='session')
def app(database):
    """Create test application"""
    from app import app
    
    # Create the actual application instance
    test_app = app
    
    test_app.config.update({
        'TESTING': True,
        'DATABASE_URL': database,
        'SERVER_NAME': 'test.local',
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'test_secret_key'
    })
    
    # Return the actual application instance, not the function
    return test_app

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
        # Add explicit cleanup for FTS table
        session.execute(text("DELETE FROM books_fts;"))
        session.commit()
    finally:
        session.rollback()
        session.close() 

@pytest.fixture
def app_context(app):
    with app.app_context():
        with app.test_request_context():
            yield

@pytest.fixture(autouse=True)
def setup_test_env(app_context):
    """Automatically set up test environment for all tests"""
    pass 

@pytest.fixture(autouse=True)
def reset_db_engine():
    """Reset database engine before each test"""
    from helper import reset_engine
    reset_engine()
    yield