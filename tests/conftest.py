import pytest
from app import create_app
from models import db, User, Book
import os
import redis
from fakeredis import FakeRedis
from flask_limiter.util import get_remote_address
from werkzeug.security import generate_password_hash
from flask_login import login_user
from sqlalchemy import text

def setup_fts(db_session):
    """Set up Full Text Search for testing if using PostgreSQL"""
    if db.engine.url.drivername == 'postgresql':
        with db.engine.connect() as conn:
            # Create the FTS configuration
            conn.execute(text("""
                CREATE EXTENSION IF NOT EXISTS unaccent;
                DROP TEXT SEARCH CONFIGURATION IF EXISTS books_fts_config;
                CREATE TEXT SEARCH CONFIGURATION books_fts_config (COPY = english);
                ALTER TEXT SEARCH CONFIGURATION books_fts_config
                    ALTER MAPPING FOR hword, hword_part, word
                    WITH unaccent, english_stem;
            """))
            
            # Create the FTS columns and index
            conn.execute(text("""
                ALTER TABLE books 
                ADD COLUMN IF NOT EXISTS search_vector tsvector 
                GENERATED ALWAYS AS (
                    setweight(to_tsvector('books_fts_config', coalesce(title, '')), 'A') ||
                    setweight(to_tsvector('books_fts_config', coalesce(authors, '')), 'B') ||
                    setweight(to_tsvector('books_fts_config', coalesce(description, '')), 'C') ||
                    setweight(to_tsvector('books_fts_config', coalesce(categories, '')), 'D')
                ) STORED;
                
                CREATE INDEX IF NOT EXISTS books_search_idx ON books USING GIN (search_vector);
            """))
            
            conn.commit()

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
    
    return test_app

@pytest.fixture(scope='function')
def db_session(app):
    """Create a fresh database session for a test"""
    with app.app_context():
        db.drop_all()
        db.create_all()
        
        # Set up PostgreSQL-specific features if needed
        setup_fts(db.session)
        
        # Return session for use in tests
        yield db.session
        
        # Clean up after test
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='function')
def client(app, db_session):
    """Create test client that maintains sessions"""
    with app.test_client() as test_client:
        with app.app_context():
            yield test_client

@pytest.fixture(scope='function')
def test_user(db_session):
    """Create a test user and add to database"""
    user = User(
        username='testuser',
        email='test@example.com',
        password=generate_password_hash('testpass123'),
        is_admin=True  # Make test user an admin by default
    )
    db_session.add(user)
    db_session.commit()
    return user

@pytest.fixture(scope='function')
def test_book(db_session, test_user):
    """Create a test book and add to database"""
    book = Book(
        user_id=test_user.id,
        title='Test Book',
        authors='Test Author',
        isbn='1234567890',
        isbn13='9781234567890',
        published_date='2024-01-01',
        status='to_read',
        description='A test book description',
        categories='Test Category'
    )
    db_session.add(book)
    db_session.commit()
    return book

@pytest.fixture(scope='function')
def auth_client(client, test_user, app):
    """Create an authenticated client"""
    with app.test_request_context():
        login_user(test_user)
    return client

@pytest.fixture(scope='function')
def redis_client():
    """Create a fake Redis client for testing"""
    fake_redis = FakeRedis(decode_responses=True)
    yield fake_redis
    fake_redis.flushall()

@pytest.fixture(autouse=True)
def patch_redis(monkeypatch, redis_client):
    """Patch Redis to use FakeRedis in tests"""
    import routes.monitoring
    monkeypatch.setattr(routes.monitoring, 'redis_client', redis_client)
    monkeypatch.setattr('routes.auth.redis_client', redis_client)

@pytest.fixture(autouse=True)
def reset_rate_limiter(app):
    """Reset rate limiter between tests"""
    from extensions import limiter
    limiter.reset()
    yield
    limiter.reset()

@pytest.fixture(autouse=True)
def app_context(app):
    """Create application context for tests"""
    with app.app_context():
        yield