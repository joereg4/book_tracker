from datetime import datetime
from models import Book, User
from flask_login import login_user
from werkzeug.security import generate_password_hash

def test_dashboard_empty(client, db_session, app):
    """Test stats dashboard with empty database"""
    # Create test user
    test_user = User(
        id=1,
        username='test_user',
        email='test@example.com',
        password=generate_password_hash('password123')
    )
    db_session.add(test_user)
    db_session.commit()

    with app.app_context():
        login_user(test_user)
        response = client.get('/stats/')
        assert response.status_code == 200
        
        # Test empty stats
        assert b'<span>Total Books</span>' in response.data
        assert b'<span class="badge bg-primary rounded-pill">0</span>' in response.data
        assert b'<span>Books Read This Year</span>' in response.data
        assert b'<span class="badge bg-success rounded-pill">0</span>' in response.data

def test_dashboard_with_books(client, db_session, app):
    """Test stats dashboard with sample books"""
    # Create test user
    test_user = User(
        id=1,
        username='test_user',
        email='test@example.com',
        password=generate_password_hash('password123')
    )
    db_session.add(test_user)
    
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
            user_id=1
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
            user_id=1
        )
    ]
    
    for book in books:
        db_session.add(book)
    db_session.commit()

    with app.app_context():
        login_user(test_user)
        
        # Test basic stats
        response = client.get('/stats/')
        assert response.status_code == 200
        assert b'<span class="badge bg-primary rounded-pill">2</span>' in response.data
        assert b'<span class="badge bg-secondary rounded-pill">500</span>' in response.data
        
        # Test year filtering
        response = client.get('/stats/?year=2024')
        assert response.status_code == 200
        assert b'[TEST] Book 1' in response.data
        assert b'January 01, 2024' in response.data

def test_dashboard_categories(client, db_session, app):
    """Test category statistics"""
    # Create test user
    test_user = User(
        id=1,
        username='test_user',
        email='test@example.com',
        password=generate_password_hash('password123')
    )
    db_session.add(test_user)
    
    # Create test books with categories
    books = [
        Book(
            title='[TEST] Category Book 1',
            authors='Test Author',
            google_books_id='cat1',
            categories='Fiction, Fantasy',
            status='read',
            user_id=1
        ),
        Book(
            title='[TEST] Category Book 2',
            authors='Test Author',
            google_books_id='cat2',
            categories='Fiction, Science Fiction',
            status='read',
            user_id=1
        )
    ]
    
    for book in books:
        db_session.add(book)
    db_session.commit()

    with app.app_context():
        login_user(test_user)
        response = client.get('/stats/')
        assert response.status_code == 200
        
        # Check categories
        assert b'Fiction' in response.data
        assert b'Fantasy' in response.data
        assert b'Science Fiction' in response.data 