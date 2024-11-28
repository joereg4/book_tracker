import pytest
import os
import sys
import tempfile
from sqlalchemy import create_engine

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
    finally:
        session.rollback()
        session.close() 