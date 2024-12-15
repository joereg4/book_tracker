import pytest
from datetime import datetime, UTC, timedelta
from flask import url_for
from models import User, db
from werkzeug.security import generate_password_hash
from routes.monitoring import record_rate_limit_hit

def test_record_rate_limit_hit(redis_client):
    """Test recording rate limit hits"""
    record_rate_limit_hit('login', '127.0.0.1')
    record_rate_limit_hit('login', '127.0.0.2')
    record_rate_limit_hit('book_search', '127.0.0.1')

    # Check data was recorded
    now = datetime.now(UTC)
    today = now.strftime('%Y-%m-%d')
    hour = now.strftime('%Y-%m-%d:%H')

    # Check login hits
    login_key = f"rate_limits:login:{today}"
    assert redis_client.hget(login_key, '127.0.0.1') == '1'
    assert redis_client.hget(login_key, '127.0.0.2') == '1'

    # Check book search hits
    book_search_key = f"rate_limits:book_search:{today}"
    assert redis_client.hget(book_search_key, '127.0.0.1') == '1'

def test_monitoring_dashboard_access(client):
    """Test access to monitoring dashboard"""
    # Unauthenticated access should redirect to login
    response = client.get('/monitoring/rate-limits')
    assert response.status_code == 302
    assert '/login' in response.location

    # Create and login user
    user = User(
        username='testuser',
        email='test@example.com',
        password=generate_password_hash('testpass123'),
        is_admin=True  # Make user admin
    )
    db.session.add(user)
    db.session.commit()

    # Get CSRF token and login
    response = client.get('/login')
    csrf_token = response.data.decode().split('name="csrf_token" value="')[1].split('"')[0]

    response = client.post('/login', data={
        'username': 'testuser',
        'password': 'testpass123',
        'csrf_token': csrf_token
    }, follow_redirects=True)

    # Authenticated access should succeed
    response = client.get('/monitoring/rate-limits')
    assert response.status_code == 200
    assert b'Rate Limit Monitoring' in response.data

def test_rate_limits_api(client, redis_client):
    """Test rate limits API endpoint"""
    # Create and login user
    user = User(
        username='testuser',
        email='test@example.com',
        password=generate_password_hash('testpass123'),
        is_admin=True  # Make user admin
    )
    db.session.add(user)
    db.session.commit()

    # Login
    response = client.get('/login')
    csrf_token = response.data.decode().split('name="csrf_token" value="')[1].split('"')[0]

    client.post('/login', data={
        'username': 'testuser',
        'password': 'testpass123',
        'csrf_token': csrf_token
    }, follow_redirects=True)

    # Record some test data
    record_rate_limit_hit('login', '127.0.0.1')
    record_rate_limit_hit('login', '127.0.0.2')
    record_rate_limit_hit('book_search', '127.0.0.1')

    # Test API response
    response = client.get('/monitoring/api/rate-limits')
    assert response.status_code == 200
    data = response.get_json()

    # Check login stats
    assert 'login' in data
    assert data['login']['today_total'] == 2
    assert '127.0.0.1' in data['login']['today_hits']
    assert '127.0.0.2' in data['login']['today_hits']

    # Check book search stats
    assert 'book_search' in data
    assert data['book_search']['today_total'] == 1
    assert '127.0.0.1' in data['book_search']['today_hits']

def test_rate_limit_integration(client, redis_client):
    """Test rate limiting integration with monitoring"""
    from extensions import limiter
    
    # Clear any existing rate limits
    now = datetime.now(UTC)
    redis_client.delete(f"login_attempts:127.0.0.1:{now.strftime('%Y-%m-%d:%H:%M')}")
    limiter.reset()

    # Create user
    user = User(
        username='testuser',
        email='test@example.com',
        password=generate_password_hash('testpass123'),
        is_admin=True  # Make user admin
    )
    db.session.add(user)
    db.session.commit()

    # Get CSRF token
    response = client.get('/login')
    csrf_token = response.data.decode().split('name="csrf_token" value="')[1].split('"')[0]

    # First login successfully to access the API
    response = client.post('/login', data={
        'username': 'testuser',
        'password': 'testpass123',
        'csrf_token': csrf_token
    }, follow_redirects=True)
    assert response.status_code == 200

    # Now logout to test rate limiting
    client.get('/logout')

    # Get a fresh CSRF token
    response = client.get('/login')
    csrf_token = response.data.decode().split('name="csrf_token" value="')[1].split('"')[0]

    # Make 5 failed login attempts
    for i in range(6):  # Try 6 times to ensure we hit the limit
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

    # Get a fresh CSRF token and login again to check API
    response = client.get('/login')
    csrf_token = response.data.decode().split('name="csrf_token" value="')[1].split('"')[0]

    # Reset rate limiter to allow login
    redis_client.delete(f"login_attempts:127.0.0.1:{now.strftime('%Y-%m-%d:%H:%M')}")
    limiter.reset()

    # Now login successfully
    response = client.post('/login', data={
        'username': 'testuser',
        'password': 'testpass123',
        'csrf_token': csrf_token
    }, follow_redirects=True)
    assert response.status_code == 200

    # Check API for recorded hits
    response = client.get('/monitoring/api/rate-limits')
    assert response.status_code == 200  # Should succeed now
    data = response.get_json()

    # Verify login attempts were recorded
    assert 'login' in data
    assert data['login']['today_total'] >= 2  # At least one successful login and one failed login
    assert '127.0.0.1' in data['login']['today_hits']