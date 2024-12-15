from models import User
from werkzeug.security import generate_password_hash
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from tests.utils import get_csrf_token, login_user

def test_rate_limit_login(client, db_session):
    """Test rate limiting on login endpoint"""
    # Create test user
    user = User(
        username='testuser',
        email='test@example.com',
        password=generate_password_hash('testpass123')
    )
    db_session.add(user)
    db_session.commit()

    # Get CSRF token
    response = client.get('/login')
    csrf_token = get_csrf_token(response)
    
    # Try multiple login attempts
    for i in range(6):  # Attempt more than the rate limit (5 per minute)
        response = client.post('/login', data={
            'username': 'testuser',
            'password': 'wrongpass',
            'csrf_token': csrf_token
        })
        
        if response.status_code == 429:  # Rate limit exceeded
            assert b'Rate limit exceeded' in response.data
            break
        else:
            assert response.status_code == 400  # Invalid credentials
    else:
        assert False, "Rate limit was not triggered"

def test_rate_limit_book_search(auth_client):
    """Test rate limiting on book search endpoint"""
    # Try multiple search attempts
    for i in range(31):  # Attempt more than the rate limit (30 per minute)
        response = auth_client.get('/books/search?q=test')

        if response.status_code == 429:  # Rate limit exceeded
            assert b'Rate limit exceeded. Please try again later.' in response.data
            break
    else:
        assert False, "Rate limit was not triggered"

def test_csrf_protection_add_book(auth_client, db_session):
    """Test CSRF protection on book addition"""
    # Try to add a book without CSRF token
    response = auth_client.post('/books/add', data={
        'id': 'test123',
        'title': 'Test Book',
        'authors': 'Test Author',
        'status': 'to_read'
    })
    
    assert response.status_code == 400
    assert b'The CSRF token is missing' in response.data
    
    # Try with invalid CSRF token
    response = auth_client.post('/books/add', data={
        'id': 'test123',
        'title': 'Test Book',
        'authors': 'Test Author',
        'status': 'to_read',
        'csrf_token': 'invalid-token'
    })
    
    assert response.status_code == 400
    assert b'The CSRF session token is missing' in response.data
    
    # Get valid CSRF token from profile page (not rate limited)
    response = auth_client.get('/profile')
    csrf_token = get_csrf_token(response)
    
    # Try with valid CSRF token
    response = auth_client.post('/books/add', data={
        'id': 'test123',
        'title': 'Test Book',
        'authors': 'Test Author',
        'status': 'to_read',
        'csrf_token': csrf_token
    })
    
    assert response.status_code == 302  # Redirect after successful addition