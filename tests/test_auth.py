import pytest
from werkzeug.security import generate_password_hash, check_password_hash
from models import User
from flask_login import current_user, login_user, LoginManager

@pytest.fixture
def app(database):
    """Create and configure a new app instance for each test."""
    from app import app
    
    # Get the Flask application instance
    test_app = app
    
    # Configure the app for testing
    test_app.config.update({
        'TESTING': True,
        'DATABASE_URL': database,
        'SERVER_NAME': 'test.local'
    })
    
    # Return the configured app
    return test_app

def test_signup_success(client, db_session):
    """Test successful signup"""
    response = client.post('/signup', data={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'testpass123',
        'confirm_password': 'testpass123'
    }, follow_redirects=True)
    
    assert b'Registration successful!' in response.data
    
    # Verify user was created in database
    user = db_session.query(User).filter_by(username='testuser').first()
    assert user is not None
    assert user.email == 'test@example.com'
    assert check_password_hash(user.password, 'testpass123')

def test_signup_validation(client, db_session):
    """Test signup validation"""
    # Test missing fields
    response = client.post('/signup', data={}, follow_redirects=True)
    assert b'All fields are required' in response.data
    
    # Test password mismatch
    response = client.post('/signup', data={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'testpass123',
        'confirm_password': 'different'
    }, follow_redirects=True)
    assert b'Passwords do not match' in response.data
    
    # Create a user for duplicate testing
    user = User(
        username='existinguser',
        email='existing@example.com',
        password=generate_password_hash('password123')
    )
    db_session.add(user)
    db_session.commit()
    
    # Test duplicate username
    response = client.post('/signup', data={
        'username': 'existinguser',
        'email': 'new@example.com',
        'password': 'password123',
        'confirm_password': 'password123'
    }, follow_redirects=True)
    assert b'Username already exists' in response.data
    
    # Test duplicate email
    response = client.post('/signup', data={
        'username': 'newuser',
        'email': 'existing@example.com',
        'password': 'password123',
        'confirm_password': 'password123'
    }, follow_redirects=True)
    assert b'Email already registered' in response.data

def test_login_success(client, db_session, app, app_context):
    """Test successful login"""
    # Create user
    user = User(
        username='testuser',
        email='test@example.com',
        password=generate_password_hash('testpass123')
    )
    db_session.add(user)
    db_session.commit()
    
    # Test login
    response = client.post('/login', data={
        'username': 'testuser',
        'password': 'testpass123'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Invalid username or password' not in response.data
    assert current_user.is_authenticated
    assert current_user.username == 'testuser'

def test_login_invalid_credentials(client, db_session):
    """Test login with wrong password"""
    # Create user
    user = User(
        username='testuser',
        email='test@example.com',
        password=generate_password_hash('password123')
    )
    db_session.add(user)
    db_session.commit()
    
    # Test wrong password
    response = client.post('/login', data={
        'username': 'testuser',
        'password': 'wrongpassword'
    }, follow_redirects=True)
    
    assert b'Invalid username or password' in response.data
    assert response.status_code == 200

def test_logout(client, auth, app_context):
    """Test logout functionality"""
    # Login first
    auth.login()
    assert current_user.is_authenticated
    
    # Test logout
    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert not current_user.is_authenticated

@pytest.fixture
def auth(client, db_session):
    """Authentication helper fixture"""
    class AuthActions:
        def login(self, username='testuser', password='password123'):
            # Create user if doesn't exist
            user = db_session.query(User).filter_by(username=username).first()
            if not user:
                user = User(
                    username=username,
                    email='test@example.com',
                    password=generate_password_hash(password)
                )
                db_session.add(user)
                db_session.commit()
            
            return client.post('/login', data={
                'username': username,
                'password': password
            }, follow_redirects=True)
    
    return AuthActions() 

def test_signup_password_match(client, db_session):
    """Test signup with matching passwords"""
    response = client.post('/signup', data={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'testpass123',
        'confirm_password': 'testpass123'
    }, follow_redirects=True)
    
    # Should succeed and redirect to login
    assert response.status_code == 200
    assert b'Registration successful!' in response.data
    
    # Verify user was created
    user = db_session.query(User).filter_by(username='testuser').first()
    assert user is not None
    assert user.email == 'test@example.com'
    assert check_password_hash(user.password, 'testpass123')

def test_signup_password_mismatch(client, db_session):
    """Test signup with non-matching passwords"""
    response = client.post('/signup', data={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'testpass123',
        'confirm_password': 'differentpass'
    }, follow_redirects=True)
    
    # Should fail with error message
    assert response.status_code == 200
    assert b'Passwords do not match' in response.data
    
    # Verify no user was created
    user = db_session.query(User).filter_by(username='testuser').first()
    assert user is None