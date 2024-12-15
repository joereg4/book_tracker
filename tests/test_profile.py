from datetime import datetime
from models import User, Book
from werkzeug.security import generate_password_hash, check_password_hash
import json
from tests.utils import get_csrf_token, login_user

def test_profile_view_authenticated(auth_client):
    """Test profile view for authenticated user"""
    response = auth_client.get('/profile')
    assert response.status_code == 200
    assert b'Profile' in response.data
    assert b'test@example.com' in response.data
    assert b'Export as CSV' in response.data

def test_profile_update_email(auth_client, db_session):
    """Test updating user email address"""
    # Get CSRF token
    response = auth_client.get('/profile')
    csrf_token = get_csrf_token(response)
    
    # Update email
    response = auth_client.post('/profile/update_email', data={
        'email': 'newemail@example.com',
        'csrf_token': csrf_token
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Email updated successfully' in response.data
    
    # Verify database update
    user = User.query.filter_by(username='testuser').first()
    assert user.email == 'newemail@example.com'

def test_profile_update_password(auth_client, db_session):
    """Test updating user password"""
    # Get CSRF token
    response = auth_client.get('/profile')
    csrf_token = get_csrf_token(response)
    
    # Update password
    response = auth_client.post('/profile/update_password', data={
        'current_password': 'testpass123',
        'new_password': 'newpass123',
        'confirm_password': 'newpass123',
        'csrf_token': csrf_token
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Password updated successfully' in response.data
    
    # Verify password was updated
    user = User.query.filter_by(username='testuser').first()
    assert check_password_hash(user.password, 'newpass123')

def test_profile_delete_account(auth_client, db_session):
    """Test account deletion functionality"""
    # Add some books for the user
    user = User.query.filter_by(username='testuser').first()
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
    
    # Get CSRF token
    response = auth_client.get('/profile')
    csrf_token = get_csrf_token(response)
    
    # Delete account
    response = auth_client.post('/profile/delete', data={
        'confirmation': 'DELETE',
        'csrf_token': csrf_token
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Your account has been permanently deleted' in response.data
    
    # Verify user and books were deleted
    assert User.query.filter_by(username='testuser').first() is None
    assert Book.query.filter_by(user_id=user.id).first() is None

def test_export_books_csv(auth_client, db_session):
    """Test CSV export functionality"""
    # Add test books
    user = User.query.filter_by(username='testuser').first()
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
    
    # Export books as CSV
    response = auth_client.get('/profile/export?format=csv')
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'text/csv; charset=utf-8'
    
    data = response.data.decode('utf-8')
    lines = data.splitlines()
    assert lines[0] == 'Title,Author,Status,Date Added,Date Read'
    assert lines[1] == 'Test Book 1,Author 1,read,2024-01-01,2024-02-01'
    assert lines[2] == 'Test Book 2,Author 2,reading,2024-01-15,'

def test_export_books_json(auth_client, db_session):
    """Test JSON export functionality"""
    # Add test books
    user = User.query.filter_by(username='testuser').first()
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
    
    # Export books as JSON
    response = auth_client.get('/profile/export?format=json')
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/json'
    
    data = json.loads(response.data)
    assert len(data) == 2
    
    # Verify first book
    assert data[0]['title'] == 'Test Book 1'
    assert data[0]['authors'] == 'Author 1'
    assert data[0]['status'] == 'read'
    assert data[0]['created_at'] == '2024-01-01'
    assert data[0]['date_read'] == '2024-02-01'
    
    # Verify second book
    assert data[1]['title'] == 'Test Book 2'
    assert data[1]['authors'] == 'Author 2'
    assert data[1]['status'] == 'reading'
    assert data[1]['created_at'] == '2024-01-15'
    assert data[1]['date_read'] is None

