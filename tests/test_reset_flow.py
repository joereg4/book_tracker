import pytest
from models import User, db
from werkzeug.security import generate_password_hash, check_password_hash

def test_password_reset_flow_live(client, db_session):
    """Test the complete password reset flow"""
    # Create a test user
    user = User(
        username='testreset',
        email='testreset@example.com',
        password=generate_password_hash('oldpassword')
    )
    db_session.add(user)
    db_session.commit()
    
    # Step 1: Request password reset
    response = client.get('/forgot-password')
    assert response.status_code == 200
    
    # Get CSRF token
    html = response.data.decode()
    csrf_token = html.split('csrf_token" value="')[1].split('"')[0]
    
    # Submit forgot password form
    response = client.post('/forgot-password', data={
        'email': 'testreset@example.com',
        'csrf_token': csrf_token
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Reset instructions sent to your email' in response.data
    
    # Verify token was generated
    user = db_session.get(User, user.id)
    assert user.reset_token is not None
    assert user.reset_token_expiry is not None
    
    reset_token = user.reset_token
    
    # Step 2: Reset password
    response = client.get(f'/reset-password/{reset_token}')
    assert response.status_code == 200
    
    # Get new CSRF token
    html = response.data.decode()
    csrf_token = html.split('csrf_token" value="')[1].split('"')[0]
    
    # Submit new password
    response = client.post(f'/reset-password/{reset_token}', data={
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
    
    print("Password reset flow test completed successfully!") 