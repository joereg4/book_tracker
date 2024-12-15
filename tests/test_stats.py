from models import User, Book
from werkzeug.security import generate_password_hash
from datetime import datetime
from tests.utils import get_csrf_token, login_user

def test_dashboard_empty(auth_client):
    """Test stats dashboard with empty database"""
    response = auth_client.get('/stats/')
    assert response.status_code == 200
    assert b'Reading Statistics' in response.data
    assert b'Total Books</span>\n                            <span class="badge bg-primary rounded-pill">0</span>' in response.data
    assert b'Total Pages Read</span>\n                            <span class="badge bg-secondary rounded-pill">0</span>' in response.data

def test_dashboard_with_books(auth_client, db_session):
    """Test stats dashboard with sample books"""
    # Get the test user
    user = User.query.filter_by(username='testuser').first()
    
    # Create test books
    books = [
        Book(
            title='[TEST] Book 1',
            authors='Author 1',
            google_books_id='test1',
            status='read',
            date_read=datetime(2024, 1, 1),
            page_count=200,
            categories='Fiction, Fantasy',
            publisher='Publisher A',
            user_id=user.id
        ),
        Book(
            title='[TEST] Book 2',
            authors='Author 1',
            google_books_id='test2',
            status='read',
            date_read=datetime(2023, 12, 1),
            page_count=300,
            categories='Fiction, Science Fiction',
            publisher='Publisher B',
            user_id=user.id
        )
    ]

    for book in books:
        db_session.add(book)
    db_session.commit()

    response = auth_client.get('/stats/')
    assert response.status_code == 200
    
    # Check reading stats
    assert b'Total Books</span>\n                            <span class="badge bg-primary rounded-pill">2</span>' in response.data
    assert b'Total Pages Read</span>\n                            <span class="badge bg-secondary rounded-pill">500</span>' in response.data
    
    # Check author stats
    assert b'Author 1' in response.data
    assert b'Most Read Author</span>\n                            <span class="badge bg-secondary">Author 1</span>' in response.data
    
    # Check publisher stats
    assert b'Most Read Publisher</span>\n                            <span class="badge bg-secondary">Publisher A</span>' in response.data
    assert b'[TEST] Book 2 (300 pages)' in response.data

def test_dashboard_categories(auth_client, db_session):
    """Test category statistics"""
    # Get the test user
    user = User.query.filter_by(username='testuser').first()
    
    # Create test books with categories
    books = [
        Book(
            title='[TEST] Category Book 1',
            authors='Test Author',
            google_books_id='cat1',
            categories='Fiction, Fantasy',
            status='read',
            user_id=user.id
        ),
        Book(
            title='[TEST] Category Book 2',
            authors='Test Author',
            google_books_id='cat2',
            categories='Fiction, Science Fiction',
            status='read',
            user_id=user.id
        )
    ]

    for book in books:
        db_session.add(book)
    db_session.commit()

    response = auth_client.get('/stats/')
    assert response.status_code == 200
    
    # Check category stats
    assert b'Fiction (2)' in response.data
    assert b'Fantasy (1)' in response.data
    assert b'Science Fiction (1)' in response.data
  