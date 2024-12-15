from models import User
from werkzeug.security import generate_password_hash
from datetime import datetime, UTC, timedelta

def test_admin_dashboard_access(client, db_session):
    """Test access to admin dashboard"""
    # Create regular user
    regular_user = User(
        username='regular',
        email='regular@example.com',
        password=generate_password_hash('testpass123')
    )
    db_session.add(regular_user)

    # Create admin user
    admin_user = User(
        username='admin',
        email='admin@example.com',
        password=generate_password_hash('testpass123'),
        is_admin=True
    )
    db_session.add(admin_user)
    db_session.commit()

    # Test unauthenticated access
    response = client.get('/admin/')
    assert response.status_code == 302  # Redirect to login
    assert '/login' in response.location

    # Login as regular user
    response = client.get('/login')
    csrf_token = response.data.decode().split('name="csrf_token" value="')[1].split('"')[0]
    
    client.post('/login', data={
        'username': 'regular',
        'password': 'testpass123',
        'csrf_token': csrf_token
    })

    # Test regular user access
    response = client.get('/admin/')
    assert response.status_code == 403  # Forbidden

    # Test admin link visibility in footer
    response = client.get('/')
    assert b'Admin Dashboard' not in response.data

    # Login as admin user
    client.get('/logout')
    response = client.get('/login')
    csrf_token = response.data.decode().split('name="csrf_token" value="')[1].split('"')[0]
    
    client.post('/login', data={
        'username': 'admin',
        'password': 'testpass123',
        'csrf_token': csrf_token
    })

    # Test admin user access
    response = client.get('/admin/')
    assert response.status_code == 200
    assert b'Admin Dashboard' in response.data

    # Test admin link visibility in footer for admin user
    response = client.get('/')
    assert b'Admin Dashboard' in response.data

def test_admin_dashboard_content(client, db_session):
    """Test admin dashboard content"""
    # Create some test users
    users = [
        User(
            username=f'user{i}',
            email=f'user{i}@example.com',
            password=generate_password_hash('testpass123'),
            is_admin=i == 0,  # First user is admin
            created_at=datetime.now(UTC) - timedelta(days=i),
            last_seen=datetime.now(UTC) - timedelta(hours=i) if i < 3 else None
        )
        for i in range(10)
    ]
    db_session.add_all(users)
    db_session.commit()

    # Login as admin
    response = client.get('/login')
    csrf_token = response.data.decode().split('name="csrf_token" value="')[1].split('"')[0]
    
    client.post('/login', data={
        'username': 'user0',
        'password': 'testpass123',
        'csrf_token': csrf_token
    })

    # Test dashboard content
    response = client.get('/admin/')
    assert response.status_code == 200

    # Check user statistics
    assert b'Total Users' in response.data
    assert str(len(users)).encode() in response.data  # Total users count
    assert b'Active Users (30d)' in response.data
    assert b'Admin Users' in response.data
    assert b'>1<' in response.data  # Admin users count

    # Check recent users table
    for i in range(5):  # Should show 5 most recent users
        assert f'user{i}'.encode() in response.data
        assert f'user{i}@example.com'.encode() in response.data

    # Check quick actions
    assert b'Rate Limits Monitor' in response.data
    assert b'href="/monitoring/rate-limits"' in response.data