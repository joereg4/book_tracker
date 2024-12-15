import pytest
from app import create_app
from models import db
import os

@pytest.fixture(scope='session')
def app():
    """Create test application"""
    # Create a new app instance for testing with explicit config
    test_app = create_app('config.TestConfig')
    
    # Additional safety check
    if not test_app.config['SQLALCHEMY_DATABASE_URI'].endswith(':memory:'):
        raise RuntimeError(
            "CRITICAL SAFETY ERROR: Tests must use in-memory database! "
            "Current URI: " + test_app.config['SQLALCHEMY_DATABASE_URI']
        )
    
    # Create tables in test database
    with test_app.app_context():
        db.drop_all()
        db.create_all()
        
    return test_app

@pytest.fixture(scope='session')
def client(app):
    return app.test_client()

@pytest.fixture(scope='function')
def db_session(app):
    """Create a new database session for a test"""
    # Additional safety check
    if not app.config['SQLALCHEMY_DATABASE_URI'].endswith(':memory:'):
        raise RuntimeError("SAFETY ERROR: Tests attempting to use non-memory database!")
        
    with app.app_context():
        db.drop_all()
        db.create_all()
        yield db.session
        db.session.remove()

@pytest.fixture(autouse=True)
def cleanup_tables(db_session):
    """Clean up tables after each test"""
    yield
    for table in reversed(db.metadata.sorted_tables):
        db_session.execute(table.delete())
    db_session.commit()