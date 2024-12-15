from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.security import generate_password_hash
from flask_wtf.csrf import generate_csrf
from models import User, db
from flask_login import current_user
from extensions import limiter
import pytest

@pytest.fixture(autouse=True)
def reset_limiter(app):
    """Reset rate limiter before each test"""
    app.config['TEST_RATE_LIMIT'] = True  # Enable rate limiting for security tests
    if hasattr(app, 'limiter'):
        app.limiter.reset()
    yield
    app.config['TEST_RATE_LIMIT'] = False  # Disable rate limiting after tests

def test_rate_limit_login(client, db_session, app):
    """Test rate limiting on login endpoint"""
    # Create test user
    user = User(
        username='testuser',
        email='test@example.com',
        password=generate_password_hash('testpass123')
    )
    db_session.add(user)
    db_session.commit()

    with client:
        # Get CSRF token
        response = client.get('/login')
        csrf_token = response.data.decode().split('name="csrf_token" value="')[1].split('"')[0]

        # Try multiple rapid logins with wrong password
        for i in range(6):  # Exceeds the 5 per minute limit
            response = client.post('/login', data={
                'username': 'testuser',
                'password': 'wrongpass',
                'csrf_token': csrf_token
            })

            if i < 5:
                assert response.status_code == 400  # Should fail with invalid credentials
            else:
                assert response.status_code == 429  # Should be rate limited

def test_rate_limit_book_search(client, db_session, app):
    """Test rate limiting on book search endpoint"""
    # Reset rate limiter storage
    limiter.reset()

    # Create test user
    user = User(
        username='testuser',
        email='test@example.com',
        password=generate_password_hash('testpass123')
    )
    db_session.add(user)
    db_session.commit()

    with client:
        # Get CSRF token and login
        response = client.get('/login')
        csrf_token = response.data.decode().split('name="csrf_token" value="')[1].split('"')[0]

        response = client.post('/login', data={
            'username': 'testuser',
            'password': 'testpass123',
            'csrf_token': csrf_token
        }, follow_redirects=True)

        assert response.status_code == 200
        assert current_user.is_authenticated

        # Try multiple rapid searches
        for i in range(32):  # Exceeds the 30 per minute limit
            response = client.get('/books/search', query_string={'q': f'test{i}'})

            if i < 30:
                assert response.status_code == 200  # Should succeed
            else:
                assert response.status_code == 429  # Should be rate limited

def test_csrf_protection_add_book(client, db_session, app):
    """Test CSRF protection on book addition"""
    # Reset rate limiter storage
    limiter.reset()

    # Set secret key for CSRF
    app.config['SECRET_KEY'] = 'test-secret-key'
    app.config['WTF_CSRF_ENABLED'] = True

    # Create test user
    user = User(
        username='testuser',
        email='test@example.com',
        password=generate_password_hash('testpass123')
    )
    db_session.add(user)
    db_session.commit()

    with client:
        # Get login page and CSRF token
        response = client.get('/login')
        assert response.status_code == 200
        csrf_token = response.data.decode().split('name="csrf_token" value="')[1].split('"')[0]

        # Login with CSRF token
        response = client.post('/login', data={
            'username': 'testuser',
            'password': 'testpass123',
            'csrf_token': csrf_token
        }, follow_redirects=True)

        assert response.status_code == 200
        assert current_user.is_authenticated

        # Try to add a book without CSRF token
        book_data = {
            'id': 'test123',
            'title': 'Test Book',
            'authors': 'Test Author'
        }
        response = client.post('/books/add', data=book_data)
        assert response.status_code == 400  # Should fail without CSRF

        # Search for a book to get the add form with CSRF token
        response = client.get('/books/search', query_string={'q': 'test'})
        assert response.status_code == 200

        # Get CSRF token from search response
        csrf_token = response.data.decode().split('name="csrf_token" value="')[1].split('"')[0]

        # Try to add a book with CSRF token
        book_data['csrf_token'] = csrf_token
        response = client.post('/books/add', data=book_data)
        assert response.status_code == 302  # Should succeed with CSRF