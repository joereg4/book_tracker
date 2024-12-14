import pytest
from werkzeug.security import generate_password_hash, check_password_hash
from models import User, db
from flask_login import current_user

def test_signup_success(client, db_session, app):
    """Test successful signup"""
    with app.app_context():
        # Get CSRF token
        response = client.get('/signup')
        csrf_token = response.data.decode().split('name="csrf_token" value="')[1].split('"')[0]

        response = client.post('/signup', data={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'confirm_password': 'testpass123',
            'csrf_token': csrf_token
        }, follow_redirects=True)
        
        assert b'Registration successful!' in response.data
        
        # Verify user was created in database
        user = db_session.query(User).filter_by(username='testuser').first()
        assert user is not None
        assert user.email == 'test@example.com'
        assert check_password_hash(user.password, 'testpass123')

def test_signup_validation(client, db_session, app):
    """Test signup validation"""
    with app.app_context():
        # Get CSRF token first
        response = client.get('/signup')
        csrf_token = response.data.decode().split('name="csrf_token" value="')[1].split('"')[0]
        
        # Test missing fields
        response = client.post('/signup', data={
            'csrf_token': csrf_token
        }, follow_redirects=True)
        assert b'All fields are required' in response.data
        
        # Test password mismatch
        response = client.post('/signup', data={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'confirm_password': 'different',
            'csrf_token': csrf_token
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
            'confirm_password': 'password123',
            'csrf_token': csrf_token
        }, follow_redirects=True)
        assert b'Username already exists' in response.data
        
        # Test duplicate email
        response = client.post('/signup', data={
            'username': 'newuser',
            'email': 'existing@example.com',
            'password': 'password123',
            'confirm_password': 'password123',
            'csrf_token': csrf_token
        }, follow_redirects=True)
        assert b'Email already registered' in response.data

def test_login_success(client, db_session, app):
    """Test successful login"""
    with app.test_request_context():
        # Create user
        user = User(
            username='testuser',
            email='test@example.com',
            password=generate_password_hash('testpass123')
        )
        db_session.add(user)
        db_session.commit()
        
        # Get CSRF token
        response = client.get('/login')
        csrf_token = response.data.decode().split('name="csrf_token" value="')[1].split('"')[0]
        
        # Test login
        response = client.post('/login', data={
            'username': 'testuser',
            'password': 'testpass123',
            'csrf_token': csrf_token
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Invalid username or password' not in response.data
        assert current_user.is_authenticated
        assert current_user.username == 'testuser'

def test_login_invalid_credentials(client, db_session, app):
    """Test login with wrong password"""
    with app.app_context():
        # Create user
        user = User(
            username='testuser',
            email='test@example.com',
            password=generate_password_hash('testpass123')
        )
        db_session.add(user)
        db_session.commit()
        
        with client:  # This activates the request context
            # Make sure we're logged out first
            client.get('/logout')
            assert not current_user.is_authenticated
            
            # Get CSRF token
            response = client.get('/login')
            csrf_token = response.data.decode().split('name="csrf_token" value="')[1].split('"')[0]
            
            # Test wrong password
            response = client.post('/login', data={
                'username': 'testuser',
                'password': 'wrongpassword',
                'csrf_token': csrf_token
            }, follow_redirects=True)
            
            assert b'Invalid username or password' in response.data
            assert not current_user.is_authenticated

def test_logout(client, auth, app):
    """Test logout functionality"""
    with app.test_request_context():
        with client:  # This activates the request context
            # Login first
            auth.login()
            
            # Test logout
            response = client.get('/logout', follow_redirects=True)
            assert not current_user.is_authenticated

@pytest.fixture
def auth(client, db_session, app):
    """Authentication helper fixture"""
    class AuthActions:
        def login(self, username='testuser', password='testpass123'):
            with app.app_context():
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
                
                # Get CSRF token
                response = client.get('/login')
                csrf_token = response.data.decode().split('name="csrf_token" value="')[1].split('"')[0]
                
                return client.post('/login', data={
                    'username': username,
                    'password': password,
                    'csrf_token': csrf_token
                }, follow_redirects=True)
    
    return AuthActions()