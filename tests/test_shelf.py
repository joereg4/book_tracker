from models import Book, User
from datetime import datetime
from sqlalchemy.sql import text
from werkzeug.security import generate_password_hash
from flask_login import login_user

def test_shelf_view_empty(client, db_session, app):
    """Test shelf view with empty database"""
    # Create test user
    test_user = User(
        id=1,
        username='test_user',
        email='test@example.com',
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
            'username': 'test_user',
            'password': 'password123',
            'csrf_token': csrf_token
        }, follow_redirects=True)
        
        # Test each shelf
        for shelf, title in [
            ('to_read', 'To Read'),
            ('reading', 'Currently Reading'),
            ('read', 'Read')
         ]:
            response = client.get(f'/shelf/{shelf}')
            assert response.status_code == 200
            assert title.encode() in response.data
            assert b'Found 0 books' not in response.data  # No search performed

def test_shelf_view_with_books(client, db_session, app):
    """Test shelf view with sample books"""
    with app.app_context():
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
                status='to_read',
                description='Test description 1',
                user_id=1
            ),
            Book(
                title='[TEST] Book 2',
                authors='Author 2',
                google_books_id='test2',
                status='reading',
                page_count=200,
                user_id=1
            ),
            Book(
                title='[TEST] Book 3',
                authors='Author 3',
                google_books_id='test3',
                status='read',
                date_read=datetime(2024, 1, 1),
                user_id=1
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
                'username': 'test_user',
                'password': 'password123',
                'csrf_token': csrf_token
            }, follow_redirects=True)

            # Verify login was successful
            assert response.status_code == 200
            assert b'Welcome back' in response.data

            # Test each shelf view
            response = client.get('/shelf/to_read')
            assert response.status_code == 200
            assert b'[TEST] Book 1' in response.data
            assert b'Author 1' in response.data
            assert b'Test description 1' in response.data

            response = client.get('/shelf/reading')
            assert response.status_code == 200
            assert b'[TEST] Book 2' in response.data
            assert b'Author 2' in response.data
            assert b'200 pages' in response.data

            response = client.get('/shelf/read')
            assert response.status_code == 200
            assert b'[TEST] Book 3' in response.data
            assert b'Author 3' in response.data
            assert b'January 01, 2024' in response.data

def test_shelf_search(client, db_session, app):
    """Test shelf search functionality"""
    with app.app_context():
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
                title='[TEST] Fantasy Book',
                authors='Author 1',
                google_books_id='test1',
                status='read',
                description='A fantasy story',
                user_id=1
            ),
            Book(
                title='[TEST] Science Book',
                authors='Author 2',
                google_books_id='test2',
                status='read',
                description='A science story',
                user_id=1
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
                'username': 'test_user',
                'password': 'password123',
                'csrf_token': csrf_token
            }, follow_redirects=True)

            # Verify login was successful
            assert response.status_code == 200
            assert b'Welcome back' in response.data

            # Test search functionality
            response = client.get('/shelf/read?search=fantasy')
            assert response.status_code == 200
            assert b'[TEST] Fantasy Book' in response.data
            assert b'[TEST] Science Book' not in response.data

            response = client.get('/shelf/read?search=science')
            assert response.status_code == 200
            assert b'[TEST] Science Book' in response.data
            assert b'[TEST] Fantasy Book' not in response.data