import pytest
from app import app as flask_app, limiter, csrf
from models import db

@pytest.fixture(scope='session')
def app():
    """Create test application"""
    flask_app.config['TESTING'] = True
    flask_app.config['WTF_CSRF_ENABLED'] = True
    flask_app.config['RATELIMIT_ENABLED'] = False
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with flask_app.app_context():
        db.drop_all()
        db.create_all()
        
    return flask_app

@pytest.fixture(scope='session')
def client(app):
    return app.test_client()

@pytest.fixture(scope='function')
def db_session(app):
    """Create a new database session for a test"""
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