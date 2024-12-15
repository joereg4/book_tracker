import pytest
from datetime import datetime, timedelta
from models import User
from werkzeug.security import generate_password_hash, check_password_hash
from flask import url_for

def get_csrf_token(response):
    """Extract CSRF token from response HTML"""
    html = response.data.decode()
    csrf_token = html.split('csrf_token" value="')[1].split('"')[0]
    return csrf_token

def test_forgot_password_request(client, db_session):
    """Test requesting a password reset"""
    # Create a user
    user = User(
        username='testuser',
        email='test@example.com',
        password=generate_password_hash('oldpassword')
    )
    db_session.add(user)
    db_session.commit()
    
    # Get CSRF token
    response = client.get('/forgot-password')
    assert response.status_code == 200
    csrf_token = get_csrf_token(response)
    
    # Request password reset
    response = client.post('/forgot-password', data={
        'email': 'test@example.com',
        'csrf_token': csrf_token
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Reset instructions sent to your email' in response.data
    
    # Verify token was generated
    user = db_session.get(User, user.id)
    assert user.reset_token is not None
    assert user.reset_token_expiry > datetime.now()

def test_forgot_password_invalid_email(client, db_session):
    """Test requesting reset with invalid email"""
    # Get CSRF token
    response = client.get('/forgot-password')
    csrf_token = get_csrf_token(response)
    
    response = client.post('/forgot-password', data={
        'email': 'nonexistent@example.com',
        'csrf_token': csrf_token
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Reset instructions sent to your email' in response.data  # Same message for security

def test_reset_password_valid_token(client, db_session):
    """Test resetting password with valid token"""
    # Create user with reset token
    user = User(
        username='testuser',
        email='test@example.com',
        password=generate_password_hash('oldpassword'),
        reset_token='validtoken123',
        reset_token_expiry=datetime.now() + timedelta(hours=1)
    )
    db_session.add(user)
    db_session.commit()
    
    # Get CSRF token
    response = client.get('/reset-password/validtoken123')
    csrf_token = get_csrf_token(response)
    
    # Reset password
    response = client.post('/reset-password/validtoken123', data={
        'password': 'newpassword123',
        'confirm_password': 'newpassword123',
        'csrf_token': csrf_token
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Password updated successfully' in response.data
    
    # Verify password was changed
    user = db_session.get(User, user.id)
    assert check_password_hash(user.password, 'newpassword123')
    assert user.reset_token is None
    assert user.reset_token_expiry is None

def test_reset_password_expired_token(client, db_session):
    """Test resetting password with expired token"""
    # Create user with expired token
    user = User(
        username='testuser',
        email='test@example.com',
        password=generate_password_hash('oldpassword'),
        reset_token='expiredtoken123',
        reset_token_expiry=datetime.now() - timedelta(hours=1)
    )
    db_session.add(user)
    db_session.commit()
    
    # Get CSRF token from login page since reset page will redirect
    response = client.get('/login')
    csrf_token = get_csrf_token(response)
    
    # Try to reset password
    response = client.post('/reset-password/expiredtoken123', data={
        'password': 'newpassword123',
        'confirm_password': 'newpassword123',
        'csrf_token': csrf_token
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Invalid or expired reset link' in response.data
    
    # Verify password was not changed
    user = db_session.get(User, user.id)
    assert check_password_hash(user.password, 'oldpassword')

def test_reset_password_invalid_token(client, db_session):
    """Test resetting password with invalid token"""
    response = client.get('/reset-password/invalidtoken123')
    assert response.status_code == 302  # Redirects to login
    
    response = client.get('/reset-password/invalidtoken123', follow_redirects=True)
    assert b'Invalid or expired reset link' in response.data

def test_reset_password_mismatch(client, db_session):
    """Test password mismatch during reset"""
    # Create user with valid token
    user = User(
        username='testuser',
        email='test@example.com',
        password=generate_password_hash('oldpassword'),
        reset_token='validtoken123',
        reset_token_expiry=datetime.now() + timedelta(hours=1)
    )
    db_session.add(user)
    db_session.commit()
    
    # Get CSRF token
    response = client.get('/reset-password/validtoken123')
    csrf_token = get_csrf_token(response)
    
    # Try to reset password with mismatch
    response = client.post('/reset-password/validtoken123', data={
        'password': 'newpassword123',
        'confirm_password': 'newpassword1234',
        'csrf_token': csrf_token
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Password mismatch' in response.data