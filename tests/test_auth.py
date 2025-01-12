from flask import url_for
from models import User
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

def get_csrf_token(response):
    """Extract CSRF token from response"""
    return response.data.decode().split('name="csrf_token" value="')[1].split('"')[0]

def test_signup_success(client, db_session):
    """Test successful user signup"""
    # Get CSRF token
    response = client.get('/signup')
    csrf_token = get_csrf_token(response)
    
    response = client.post('/signup', data={
        'username': 'newuser',
        'email': 'new@example.com',
        'password': 'Test123!@#',  # Strong password meeting all requirements
        'confirm_password': 'Test123!@#',
        'csrf_token': csrf_token
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Account created successfully!' in response.data
    
    # Verify user was created
    user = User.query.filter_by(username='newuser').first()
    assert user is not None
    assert user.email == 'new@example.com'
    assert check_password_hash(user.password, 'Test123!@#')

def test_signup_validation(client, db_session):
    """Test signup validation"""
    # Get CSRF token
    response = client.get('/signup')
    csrf_token = get_csrf_token(response)
    
    # Test missing fields
    response = client.post('/signup', data={
        'csrf_token': csrf_token
    }, follow_redirects=True)
    assert b'All fields are required' in response.data
    
    # Test password mismatch
    response = client.post('/signup', data={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'Test123!@#',
        'confirm_password': 'Test123!@#different',
        'csrf_token': csrf_token
    }, follow_redirects=True)
    assert b'Passwords do not match' in response.data

def test_password_strength(client, db_session):
    """Test password strength requirements"""
    response = client.get('/signup')
    csrf_token = get_csrf_token(response)
    
    # Test too short password
    response = client.post('/signup', data={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'Abc1!',
        'confirm_password': 'Abc1!',
        'csrf_token': csrf_token
    }, follow_redirects=True)
    assert b'Password must be at least 8 characters long' in response.data
    
    # Test missing letter
    response = client.post('/signup', data={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': '12345678!@#',
        'confirm_password': '12345678!@#',
        'csrf_token': csrf_token
    }, follow_redirects=True)
    assert b'Password must contain at least one letter' in response.data
    
    # Test missing number
    response = client.post('/signup', data={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'Abcdefgh!@#',
        'confirm_password': 'Abcdefgh!@#',
        'csrf_token': csrf_token
    }, follow_redirects=True)
    assert b'Password must contain at least one number' in response.data
    
    # Test missing special character
    response = client.post('/signup', data={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'Abcdefgh123',
        'confirm_password': 'Abcdefgh123',
        'csrf_token': csrf_token
    }, follow_redirects=True)
    assert b'Password must contain at least one special character' in response.data
    
    # Test duplicate username
    user = User(
        username='existinguser',
        email='existing@example.com',
        password=generate_password_hash('Test123!@#')
    )
    db_session.add(user)
    db_session.commit()
    
    response = client.post('/signup', data={
        'username': 'existinguser',
        'email': 'new@example.com',
        'password': 'Test123!@#',
        'confirm_password': 'Test123!@#',
        'csrf_token': csrf_token
    }, follow_redirects=True)
    assert b'Username already exists' in response.data

def test_login_success(client, test_user):
    """Test successful login"""
    # Get CSRF token
    response = client.get('/login')
    csrf_token = get_csrf_token(response)
    
    response = client.post('/login', data={
        'username': 'testuser',
        'password': 'testpass123',
        'csrf_token': csrf_token
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Welcome back!' in response.data

def test_login_invalid_credentials(client, test_user):
    """Test login with invalid credentials"""
    # Get CSRF token
    response = client.get('/login')
    csrf_token = get_csrf_token(response)
    
    response = client.post('/login', data={
        'username': 'testuser',
        'password': 'wrongpass',
        'csrf_token': csrf_token
    })
    
    assert response.status_code == 400
    assert b'Invalid username or password' in response.data

def test_logout(auth_client):
    """Test logout functionality"""
    response = auth_client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    
    # Try accessing protected page after logout
    response = auth_client.get('/profile')
    assert response.status_code == 302  # Should redirect to login