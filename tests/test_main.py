from datetime import datetime
from models import Book, User
from werkzeug.security import generate_password_hash

def test_index_empty(client):
    """Test index view with empty database"""
    response = client.get('/')
    assert response.status_code == 200
    
    # Check welcome message for non-authenticated users
    assert b'Welcome to Book Tracker' in response.data
    assert b'Keep track of your reading journey' in response.data
    assert b'Login' in response.data
    assert b'Sign Up' in response.data

def test_index_empty_authenticated(client, db_session, app):
    """Test index view with authenticated user but no books"""
    with app.test_request_context():
        # Create test user
        user = User(
            username='testuser',
            email='test@example.com',
            password=generate_password_hash('testpass')
        )
        db_session.add(user)
        db_session.commit()

        with client:
            # Get CSRF token
            response = client.get('/login')
            csrf_token = response.data.decode().split('name="csrf_token" value="')[1].split('"')[0]

            # Login with CSRF token
            response = client.post('/login', data={
                'username': 'testuser',
                'password': 'testpass',
                'csrf_token': csrf_token
            }, follow_redirects=True)

            # Now get the index page
            response = client.get('/')
            assert response.status_code == 200
            
            # Add debug print statement
            print(f"Response data: {response.data.decode()}")
            
            # Check authenticated user view
            assert b'Reading Overview' in response.data
            assert b'Currently Reading' in response.data
            assert b'Quick Actions' in response.data

def test_index_with_books(client, db_session, app):
    """Test index view with books"""
    with app.test_request_context():
        # Create and login test user
        user = User(
            username='testuser',
            email='test@example.com',
            password=generate_password_hash('testpass')
        )
        db_session.add(user)
        db_session.commit()

        with client:
            # Get CSRF token
            response = client.get('/login')
            csrf_token = response.data.decode().split('name="csrf_token" value="')[1].split('"')[0]

            # Login with CSRF token
            response = client.post('/login', data={
                'username': 'testuser',
                'password': 'testpass',
                'csrf_token': csrf_token
            }, follow_redirects=True)

            # Create test books with user_id
            books = [
                Book(
                    title='[TEST] Reading Book',
                    authors='Author 1',
                    google_books_id='test1',
                    status='reading',
                    user_id=user.id
                ),
                Book(
                    title='[TEST] To Read Book 1',
                    authors='Author 2',
                    google_books_id='test2',
                    status='to_read',
                    created_at=datetime(2024, 1, 1),
                    user_id=user.id
                ),
                Book(
                    title='[TEST] To Read Book 2',
                    authors='Author 3',
                    google_books_id='test3',
                    status='to_read',
                    created_at=datetime(2024, 1, 2),
                    user_id=user.id
                ),
                Book(
                    title='[TEST] Read Book',
                    authors='Author 4',
                    google_books_id='test4',
                    status='read',
                    date_read=datetime(2024, 1, 1),
                    user_id=user.id
                )
            ]
            for book in books:
                db_session.add(book)
            db_session.commit()
            
            response = client.get('/')
            assert response.status_code == 200
            
            # Check reading overview counts
            assert b'<span class="badge bg-primary rounded-pill">2</span>' in response.data  # To Read
            assert b'<span class="badge bg-secondary rounded-pill">1</span>' in response.data  # Reading
            assert b'<span class="badge bg-success rounded-pill">1</span>' in response.data  # Read
            
            # Check currently reading section
            assert b'[TEST] Reading Book' in response.data
            assert b'Author 1' in response.data
            assert b'Mark as Complete' in response.data
            
            # Check recently added section
            assert b'[TEST] To Read Book 1' in response.data
            assert b'[TEST] To Read Book 2' in response.data
            assert b'Start Reading' in response.data