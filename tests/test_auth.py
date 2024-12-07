import pytest
from werkzeug.security import generate_password_hash, check_password_hash
from models import User
from flask_login import current_user

def test_signup(client, db_session):
    """Test user registration"""
    # Test successful signup
    response = client.post('/signup', data={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'password123'
    }, follow_redirects=True)
    
    assert b'Registration successful!' in response.data
    
    # Verify user was created
    user = db_session.query(User).filter_by(username='testuser').first()
    assert user is not None
    assert user.email == 'test@example.com'
    assert check_password_hash(user.password, 'password123')

def test_duplicate_username(client, db_session):
    """Test signup with existing username"""
    # Create initial user
    user = User(
        username='testuser',
        email='original@example.com',
        password=generate_password_hash('password123')
    )
    db_session.add(user)
    db_session.commit()
    
    # Try to create duplicate username
    response = client.post('/signup', data={
        'username': 'testuser',
        'email': 'new@example.com',
        'password': 'password123'
    }, follow_redirects=True)
    
    assert b'Username already exists' in response.data

def test_duplicate_email(client, db_session):
    """Test signup with existing email"""
    # Create initial user
    user = User(
        username='original',
        email='test@example.com',
        password=generate_password_hash('password123')
    )
    db_session.add(user)
    db_session.commit()
    
    # Try to create duplicate email
    response = client.post('/signup', data={
        'username': 'newuser',
        'email': 'test@example.com',
        'password': 'password123'
    }, follow_redirects=True)
    
    assert b'Email already registered' in response.data

def test_login_success(client, db_session):
    """Test successful login"""
    # Create user
    user = User(
        username='testuser',
        email='test@example.com',
        password=generate_password_hash('password123')
    )
    db_session.add(user)
    db_session.commit()
    
    # Test login
    response = client.post('/login', data={
        'username': 'testuser',
        'password': 'password123'
    }, follow_redirects=True)
    
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
    assert not current_user.is_authenticated

def test_logout(client, auth):
    """Test logout functionality"""
    # Login first
    auth.login()
    
    # Test logout
    response = client.get('/logout', follow_redirects=True)
    
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