from datetime import datetime
from models import User, Book
from werkzeug.security import generate_password_hash
import json

def test_profile_view_authenticated(client, db_session, app):
    """Test profile view for authenticated user"""
    # Create test user
    user = User(
        id=1,  # Add explicit ID
        username='testuser',
        email='test@example.com',
        password=generate_password_hash('testpass'),
        created_at=datetime(2024, 1, 1)  # Set specific date for testing
    )
    db_session.add(user)
    db_session.commit()

    with client:  # This creates a request context
        # Get CSRF token
        response = client.get('/login')
        csrf_token = response.data.decode().split('name="csrf_token" value="')[1].split('"')[0]

        # Login with CSRF token
        response = client.post('/login', data={
            'username': 'testuser',
            'password': 'testpass',
            'csrf_token': csrf_token
        }, follow_redirects=True)

        # Get profile page
        response = client.get('/profile')
        assert response.status_code == 200
        
        # Check basic profile information
        assert b'testuser' in response.data
        assert b'test@example.com' in response.data
        assert b'January 01, 2024' in response.data

def test_profile_view_unauthenticated(client):
    """Test profile view redirects for unauthenticated users"""
    response = client.get('/profile', follow_redirects=True)
    
    # Should redirect to login page
    assert response.status_code == 200
    assert b'Please log in to access this page.' in response.data
    assert b'Login' in response.data

def test_profile_update_email(client, db_session, app):
    """Test updating user email address"""
    # Create test user
    user = User(
        id=1,  # Add explicit ID
        username='testuser',
        email='test@example.com',
        password=generate_password_hash('testpass')
    )
    db_session.add(user)
    db_session.commit()

    with client:  # This creates a request context
        # Get CSRF token for login
        response = client.get('/login')
        csrf_token = response.data.decode().split('name="csrf_token" value="')[1].split('"')[0]

        # Login with CSRF token
        response = client.post('/login', data={
            'username': 'testuser',
            'password': 'testpass',
            'csrf_token': csrf_token
        }, follow_redirects=True)

        # Get CSRF token for email update
        response = client.get('/profile')
        csrf_token = response.data.decode().split('name="csrf_token" value="')[1].split('"')[0]

        # Test updating email
        response = client.post('/profile/update_email', data={
            'email': 'newemail@example.com',
            'csrf_token': csrf_token
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Email updated successfully.' in response.data
        assert b'newemail@example.com' in response.data

        # Verify database was updated
        updated_user = db_session.get(User, user.id)
        assert updated_user.email == 'newemail@example.com'

        # Test empty email submission
        response = client.post('/profile/update_email', data={
            'email': '',
            'csrf_token': csrf_token
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Email is required.' in response.data
        
        # Verify email wasn't changed
        unchanged_user = db_session.get(User, user.id)
        assert unchanged_user.email == 'newemail@example.com'

def test_profile_update_password(client, db_session, app):
    """Test updating user password"""
    # Create test user
    user = User(
        id=1,  # Add explicit ID
        username='testuser',
        email='test@example.com',
        password=generate_password_hash('testpass')
    )
    db_session.add(user)
    db_session.commit()

    with client:  # This creates a request context
        # Get CSRF token for login
        response = client.get('/login')
        csrf_token = response.data.decode().split('name="csrf_token" value="')[1].split('"')[0]

        # Login with CSRF token
        response = client.post('/login', data={
            'username': 'testuser',
            'password': 'testpass',
            'csrf_token': csrf_token
        }, follow_redirects=True)

        # Get CSRF token for password update
        response = client.get('/profile')
        csrf_token = response.data.decode().split('name="csrf_token" value="')[1].split('"')[0]

        # Test updating password
        response = client.post('/profile/update_password', data={
            'current_password': 'testpass',
            'new_password': 'newpass123',
            'confirm_password': 'newpass123',
            'csrf_token': csrf_token
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Password updated successfully.' in response.data

        # Verify we can login with new password
        client.get('/logout', follow_redirects=True)
        
        # Get new CSRF token for login
        response = client.get('/login')
        csrf_token = response.data.decode().split('name="csrf_token" value="')[1].split('"')[0]
        
        response = client.post('/login', data={
            'username': 'testuser',
            'password': 'newpass123',
            'csrf_token': csrf_token
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'testuser' in response.data

        # Get CSRF token for password tests
        response = client.get('/profile')
        csrf_token = response.data.decode().split('name="csrf_token" value="')[1].split('"')[0]

        # Test with incorrect current password
        response = client.post('/profile/update_password', data={
            'current_password': 'wrongpass',
            'new_password': 'newpass456',
            'confirm_password': 'newpass456',
            'csrf_token': csrf_token
        }, follow_redirects=True)
        assert b'Current password is incorrect.' in response.data

        # Test with mismatched new passwords
        response = client.post('/profile/update_password', data={
            'current_password': 'newpass123',
            'new_password': 'newpass456',
            'confirm_password': 'different456',
            'csrf_token': csrf_token
        }, follow_redirects=True)
        assert b'New passwords do not match.' in response.data

        # Test with empty fields
        response = client.post('/profile/update_password', data={
            'current_password': '',
            'new_password': '',
            'confirm_password': '',
            'csrf_token': csrf_token
        }, follow_redirects=True)
        assert b'All password fields are required.' in response.data

def test_profile_delete_account(client, db_session, app):
    """Test account deletion functionality"""
    # Create test user with some books
    user = User(
        id=1,  # Add explicit ID
        username='testuser',
        email='test@example.com',
        password=generate_password_hash('testpass')
    )
    db_session.add(user)
    db_session.commit()

    user_id = user.id  # Store the ID for later checking

    # Add some books for the user
    books = [
        Book(
            title='Test Book 1',
            authors='Author 1',
            google_books_id='test1',
            status='reading',
            user_id=user.id
        ),
        Book(
            title='Test Book 2',
            authors='Author 2',
            google_books_id='test2',
            status='to_read',
            user_id=user.id
        )
    ]
    for book in books:
        db_session.add(book)
    db_session.commit()

    with client:  # This creates a request context
        # Get CSRF token for login
        response = client.get('/login')
        csrf_token = response.data.decode().split('name="csrf_token" value="')[1].split('"')[0]

        # Login with CSRF token
        response = client.post('/login', data={
            'username': 'testuser',
            'password': 'testpass',
            'csrf_token': csrf_token
        }, follow_redirects=True)

        # Test GET request - should show confirmation page
        response = client.get('/profile/delete')
        assert response.status_code == 200
        assert b'Delete Account' in response.data
        assert b'This action cannot be reversed' in response.data
        assert b'Type DELETE to confirm' in response.data

        # Get CSRF token for deletion
        csrf_token = response.data.decode().split('name="csrf_token" value="')[1].split('"')[0]

        # Test invalid confirmation text
        response = client.post('/profile/delete', data={
            'confirmation': 'WRONG',
            'csrf_token': csrf_token
        }, follow_redirects=True)
        assert b'Please type DELETE to confirm account deletion.' in response.data
        
        # Verify user and books still exist
        assert db_session.get(User, user_id) is not None
        assert len(db_session.get(User, user_id).books) == 2

        # Test successful deletion
        response = client.post('/profile/delete', data={
            'confirmation': 'DELETE',
            'csrf_token': csrf_token
        }, follow_redirects=True)
        assert b'Your account has been permanently deleted.' in response.data
        
        # Refresh the session to see the changes
        db_session.expire_all()
        db_session.commit()
        
        # Verify user and their books are gone
        assert db_session.get(User, user_id) is None
        
        # Verify we're logged out (check for login link)
        assert b'Login' in response.data

def test_export_books_csv(client, db_session, app):
    """Test CSV export functionality"""
    # Create test user with books
    user = User(
        id=1,  # Add explicit ID
        username='testuser',
        email='test@example.com',
        password=generate_password_hash('testpass')
    )
    db_session.add(user)
    db_session.commit()

    # Add test books
    books = [
        Book(
            title='Test Book 1',
            authors='Author 1',
            status='read',
            created_at=datetime(2024, 1, 1),
            date_read=datetime(2024, 2, 1),
            user_id=user.id
        ),
        Book(
            title='Test Book 2',
            authors='Author 2',
            status='reading',
            created_at=datetime(2024, 1, 15),
            user_id=user.id
        )
    ]
    for book in books:
        db_session.add(book)
    db_session.commit()

    with client:  # This creates a request context
        # Get CSRF token for login
        response = client.get('/login')
        csrf_token = response.data.decode().split('name="csrf_token" value="')[1].split('"')[0]

        # Login with CSRF token
        response = client.post('/login', data={
            'username': 'testuser',
            'password': 'testpass',
            'csrf_token': csrf_token
        }, follow_redirects=True)
        assert b'Welcome back' in response.data

        # Verify we're logged in by accessing profile
        response = client.get('/profile', follow_redirects=True)
        assert response.status_code == 200
        assert b'testuser' in response.data

        # Test export
        response = client.get('/profile/export')
        assert response.status_code == 200
        assert response.mimetype == 'text/csv'
        
        # Check CSV content
        csv_data = response.data.decode('utf-8')
        assert 'Title,Author,Status,Date Added,Date Read' in csv_data
        assert 'Test Book 1,Author 1,read,2024-01-01,2024-02-01' in csv_data
        assert 'Test Book 2,Author 2,reading,2024-01-15,' in csv_data

def test_export_books_json(client, db_session, app):
    """Test JSON export functionality"""
    # Create test user with books
    user = User(
        id=1,  # Add explicit ID
        username='testuser',
        email='test@example.com',
        password=generate_password_hash('testpass')
    )
    db_session.add(user)
    db_session.commit()

    # Add test books
    books = [
        Book(
            title='Test Book 1',
            authors='Author 1',
            status='read',
            created_at=datetime(2024, 1, 1),
            date_read=datetime(2024, 2, 1),
            user_id=user.id
        ),
        Book(
            title='Test Book 2',
            authors='Author 2',
            status='reading',
            created_at=datetime(2024, 1, 15),
            user_id=user.id
        )
    ]
    for book in books:
        db_session.add(book)
    db_session.commit()

    with client:  # This creates a request context
        # Get CSRF token for login
        response = client.get('/login')
        csrf_token = response.data.decode().split('name="csrf_token" value="')[1].split('"')[0]

        # Login with CSRF token
        response = client.post('/login', data={
            'username': 'testuser',
            'password': 'testpass',
            'csrf_token': csrf_token
        }, follow_redirects=True)
        assert b'Welcome back' in response.data

        # Verify we're logged in by accessing profile
        response = client.get('/profile', follow_redirects=True)
        assert response.status_code == 200
        assert b'testuser' in response.data

        # Test JSON export
        response = client.get('/profile/export?format=json')
        assert response.status_code == 200
        assert response.mimetype == 'application/json'
        
        # Parse JSON response
        data = json.loads(response.data.decode('utf-8'))
        assert len(data) == 2
        
        # Check first book
        assert data[0]['title'] == 'Test Book 1'
        assert data[0]['authors'] == 'Author 1'
        assert data[0]['status'] == 'read'
        assert data[0]['created_at'].startswith('2024-01-01')
        assert data[0]['date_read'].startswith('2024-02-01')
        
        # Check second book
        assert data[1]['title'] == 'Test Book 2'
        assert data[1]['authors'] == 'Author 2'
        assert data[1]['status'] == 'reading'
        assert data[1]['created_at'].startswith('2024-01-15')
        assert data[1]['date_read'] is None

