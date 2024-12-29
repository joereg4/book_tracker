from models import User, Book
from werkzeug.security import generate_password_hash
from datetime import datetime
from tests.utils import get_csrf_token, login_user

def test_index_empty(client):
    """Test index view for unauthenticated user"""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Track Your Reading Journey' in response.data
    assert b'Login' in response.data
    assert b'Sign Up' in response.data

def test_index_empty_authenticated(auth_client):
    """Test index view with authenticated user but no books"""
    response = auth_client.get('/')
    assert response.status_code == 200
    assert b'Reading Overview' in response.data
    assert b'No books currently being read' in response.data
    assert b'Add New Book' in response.data

def test_index_with_books(auth_client, db_session):
    """Test index view with books"""
    # Get the test user
    user = User.query.filter_by(username='testuser').first()
    
    # Add test books
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
    
    response = auth_client.get('/')
    assert response.status_code == 200
    assert b'Test Book 1' in response.data
    assert b'Test Book 2' in response.data
    assert b'Author 1' in response.data
    assert b'Author 2' in response.data