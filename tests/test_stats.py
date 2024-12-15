from datetime import datetime
from models import Book, User, db
from flask_login import login_user
from werkzeug.security import generate_password_hash

def test_dashboard_empty(client, db_session, app):
    """Test stats dashboard with empty database"""
    # Create test user
    test_user = User(
        id=1,
        username='test_user1',
        email='test1@example.com',
        password=generate_password_hash('password123')
    )
    db_session.add(test_user)
    db_session.commit()

    with client:  # This creates a request context
        # Get CSRF token
        response = client.get('/login')
        csrf_token = response.data.decode().split('name="csrf_token" value="')[1].split('"')[0]

        # Login via POST request with CSRF token
        response = client.post('/login', data={
            'username': 'test_user1',
            'password': 'password123',
            'csrf_token': csrf_token
        }, follow_redirects=True)

        # Verify login was successful
        assert response.status_code == 200
        assert b'Welcome back' in response.data

        # Test empty dashboard
        response = client.get('/stats/')
        assert response.status_code == 200
        assert b'<span>Total Books</span>' in response.data
        assert b'<span class="badge bg-primary rounded-pill">0</span>' in response.data
        assert b'<span>Books Read This Year</span>' in response.data
        assert b'<span class="badge bg-success rounded-pill">0</span>' in response.data
        assert b'<span>Total Pages Read</span>' in response.data
        assert b'<span class="badge bg-secondary rounded-pill">0</span>' in response.data

def test_dashboard_with_books(client, db_session, app):
    """Test stats dashboard with sample books"""
    # Create test user
    test_user = User(
        id=2,
        username='test_user2',
        email='test2@example.com',
        password=generate_password_hash('password123')
    )
    db_session.add(test_user)
    db_session.commit()
    
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
            user_id=2
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
            user_id=2
        )
    ]
    
    for book in books:
        db_session.add(book)
    db_session.commit()

    with client:  # This creates a request context
        # Get CSRF token
        response = client.get('/login')
        csrf_token = response.data.decode().split('name="csrf_token" value="')[1].split('"')[0]

        # Login via POST request with CSRF token
        response = client.post('/login', data={
            'username': 'test_user2',
            'password': 'password123',
            'csrf_token': csrf_token
        }, follow_redirects=True)

        # Verify login was successful
        assert response.status_code == 200
        assert b'Welcome back' in response.data

        # Test basic stats
        response = client.get('/stats/')
        assert response.status_code == 200
        assert b'<span>Total Books</span>' in response.data
        assert b'<span class="badge bg-primary rounded-pill">2</span>' in response.data
        assert b'<span>Books Read This Year</span>' in response.data
        assert b'<span class="badge bg-success rounded-pill">1</span>' in response.data
        assert b'<span>Total Pages Read</span>' in response.data
        assert b'<span class="badge bg-secondary rounded-pill">500</span>' in response.data

        # Test author stats
        assert b'<span>Most Read Author</span>' in response.data
        assert b'<span class="badge bg-secondary">Author 1</span>' in response.data

def test_dashboard_categories(client, db_session, app):
    """Test category statistics"""
    # Create test user
    test_user = User(
        id=3,
        username='test_user3',
        email='test3@example.com',
        password=generate_password_hash('password123')
    )
    db_session.add(test_user)
    db_session.commit()
    
    # Create test books with categories
    books = [
        Book(
            title='[TEST] Category Book 1',
            authors='Test Author',
            google_books_id='cat1',
            categories='Fiction, Fantasy',
            status='read',
            user_id=3
        ),
        Book(
            title='[TEST] Category Book 2',
            authors='Test Author',
            google_books_id='cat2',
            categories='Fiction, Science Fiction',
            status='read',
            user_id=3
        )
    ]
    
    for book in books:
        db_session.add(book)
    db_session.commit()

    with client:  # This creates a request context
        # Get CSRF token
        response = client.get('/login')
        csrf_token = response.data.decode().split('name="csrf_token" value="')[1].split('"')[0]

        # Login via POST request with CSRF token
        response = client.post('/login', data={
            'username': 'test_user3',
            'password': 'password123',
            'csrf_token': csrf_token
        }, follow_redirects=True)

        # Verify login was successful
        assert response.status_code == 200
        assert b'Welcome back' in response.data

        # Test category stats
        response = client.get('/stats/')
        assert response.status_code == 200
        assert b'Fiction' in response.data
        assert b'Fantasy' in response.data
        assert b'Science Fiction' in response.data
  