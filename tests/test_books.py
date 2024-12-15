from models import Book
from datetime import datetime
from werkzeug.security import generate_password_hash
from utils.text import strip_html_tags
from unittest.mock import patch
from models import User
from extensions import db

def get_csrf_token(response):
    """Extract CSRF token from response"""
    return response.data.decode().split('name="csrf_token" value="')[1].split('"')[0]

def login_user(client, username, password):
    """Helper function to log in a user"""
    response = client.get('/login')
    csrf_token = get_csrf_token(response)
    return client.post('/login', data={
        'username': username,
        'password': password,
        'csrf_token': csrf_token
    }, follow_redirects=True)

def test_strip_html_tags():
    """Test HTML tag stripping utility"""
    assert strip_html_tags("<p>Test</p>") == "Test"
    assert strip_html_tags("<b>Bold</b> and <i>italic</i>") == "Bold and italic"
    assert strip_html_tags("No tags here") == "No tags here"

@patch('extensions.limiter.enabled', False)  # Disable rate limiting for tests
def test_add_book(auth_client, db_session):
    """Test adding a book"""
    # Create test user
    user = User(
        username='testuser1',
        email='test1@example.com',
        password=generate_password_hash('testpass123')
    )
    db_session.add(user)
    db_session.commit()

    # Log in the user
    login_user(auth_client, 'testuser1', 'testpass123')

    # Get CSRF token from search page
    response = auth_client.get('/books/search')
    csrf_token = get_csrf_token(response)
    
    # Test adding a book
    book_data = {
        'csrf_token': csrf_token,
        'id': 'test123',
        'title': '[TEST] Python Programming',
        'authors': 'Test Author',
        'published_date': '2024',
        'description': 'A test book about Python',
        'page_count': '200',
        'categories': 'Computers, Programming',
        'thumbnail': 'https://example.com/thumb.jpg',
        'status': 'to_read'
    }
    
    response = auth_client.post('/books/add', data=book_data)
    assert response.status_code == 302  # Redirect after successful add
    
    # Verify book was added to database
    book = Book.query.filter_by(google_books_id='test123').first()
    assert book is not None
    assert book.title == '[TEST] Python Programming'
    assert book.authors == 'Test Author'
    assert book.status == 'to_read'
    assert book.user_id == user.id

def test_update_status(auth_client, db_session):
    """Test updating book status"""
    # Create test user
    user = User(
        username='testuser2',
        email='test2@example.com',
        password=generate_password_hash('testpass123')
    )
    db_session.add(user)
    db_session.commit()

    # Log in the user
    login_user(auth_client, 'testuser2', 'testpass123')

    # Create test book
    book = Book(
        google_books_id='test123',
        title='Test Book',
        authors='Test Author',
        status='to_read',
        user_id=user.id
    )
    db_session.add(book)
    db_session.commit()
    
    # Get CSRF token
    response = auth_client.get(f'/books/book/{book.id}')
    csrf_token = get_csrf_token(response)
    
    # Test status update
    response = auth_client.post(f'/books/update_status/{book.id}', data={
        'csrf_token': csrf_token,
        'status': 'reading'
    })
    assert response.status_code == 302  # Redirect after successful update
    
    # Verify status was updated
    book = db.session.get(Book, book.id)
    assert book.status == 'reading'

def test_book_detail(auth_client, db_session):
    """Test book detail view"""
    # Create test user
    user = User(
        username='testuser3',
        email='test3@example.com',
        password=generate_password_hash('testpass123')
    )
    db_session.add(user)
    db_session.commit()

    # Log in the user
    login_user(auth_client, 'testuser3', 'testpass123')

    # Create test book
    book = Book(
        google_books_id='test123',
        title='Test Book',
        authors='Test Author',
        status='to_read',
        user_id=user.id
    )
    db_session.add(book)
    db_session.commit()
    
    # Test detail view
    response = auth_client.get(f'/books/book/{book.id}')
    assert response.status_code == 200
    assert b'Test Book' in response.data
    assert b'Test Author' in response.data

def test_update_status_without_csrf(auth_client, db_session):
    """Test updating book status without CSRF token"""
    # Create test user
    user = User(
        username='testuser4',
        email='test4@example.com',
        password=generate_password_hash('testpass123')
    )
    db_session.add(user)
    db_session.commit()

    # Log in the user
    login_user(auth_client, 'testuser4', 'testpass123')

    # Create test book
    book = Book(
        google_books_id='test123',
        title='Test Book',
        authors='Test Author',
        status='to_read',
        user_id=user.id
    )
    db_session.add(book)
    db_session.commit()
    
    # Test status update without CSRF token
    response = auth_client.post(f'/books/update_status/{book.id}', data={
        'status': 'reading'
    })
    assert response.status_code == 400
    
    # Verify status was not updated
    book = db.session.get(Book, book.id)
    assert book.status == 'to_read'

def test_update_status_with_invalid_csrf(auth_client, db_session):
    """Test updating book status with invalid CSRF token"""
    # Create test user
    user = User(
        username='testuser5',
        email='test5@example.com',
        password=generate_password_hash('testpass123')
    )
    db_session.add(user)
    db_session.commit()

    # Log in the user
    login_user(auth_client, 'testuser5', 'testpass123')

    # Create test book
    book = Book(
        google_books_id='test123',
        title='Test Book',
        authors='Test Author',
        status='to_read',
        user_id=user.id
    )
    db_session.add(book)
    db_session.commit()
    
    # Test status update with invalid CSRF token
    response = auth_client.post(f'/books/update_status/{book.id}', data={
        'csrf_token': 'invalid',
        'status': 'reading'
    })
    assert response.status_code == 400
    
    # Verify status was not updated
    book = db.session.get(Book, book.id)
    assert book.status == 'to_read'

def test_update_status_all_transitions(auth_client, db_session):
    """Test all possible status transitions"""
    # Create test user
    user = User(
        username='testuser6',
        email='test6@example.com',
        password=generate_password_hash('testpass123')
    )
    db_session.add(user)
    db_session.commit()

    # Log in the user
    login_user(auth_client, 'testuser6', 'testpass123')

    # Create test book
    book = Book(
        google_books_id='test123',
        title='Test Book',
        authors='Test Author',
        status='to_read',
        user_id=user.id
    )
    db_session.add(book)
    db_session.commit()
    
    # Get CSRF token
    response = auth_client.get(f'/books/book/{book.id}')
    csrf_token = get_csrf_token(response)
    
    # Test all transitions
    transitions = ['reading', 'read', 'to_read']
    for new_status in transitions:
        response = auth_client.post(f'/books/update_status/{book.id}', data={
            'csrf_token': csrf_token,
            'status': new_status
        })
        assert response.status_code == 302  # Redirect after successful update
        book = db.session.get(Book, book.id)
        assert book.status == new_status

def test_update_status_remove_book(auth_client, db_session):
    """Test removing a book"""
    # Create test user
    user = User(
        username='testuser7',
        email='test7@example.com',
        password=generate_password_hash('testpass123')
    )
    db_session.add(user)
    db_session.commit()

    # Log in the user
    login_user(auth_client, 'testuser7', 'testpass123')

    # Create test book
    book = Book(
        google_books_id='test123',
        title='Test Book',
        authors='Test Author',
        status='to_read',
        user_id=user.id
    )
    db_session.add(book)
    db_session.commit()
    
    # Get CSRF token
    response = auth_client.get(f'/books/book/{book.id}')
    csrf_token = get_csrf_token(response)
    
    # Test book removal
    response = auth_client.post(f'/books/update_status/{book.id}', data={
        'csrf_token': csrf_token,
        'status': 'remove'
    })
    assert response.status_code == 302  # Redirect after successful update
    
    # Verify book was removed
    book = db.session.get(Book, book.id)
    assert book is None

@patch('extensions.limiter.enabled', False)  # Disable rate limiting for tests
def test_book_search(auth_client, db_session):
    """Test book search functionality"""
    # Create test user
    user = User(
        username='testuser8',
        email='test8@example.com',
        password=generate_password_hash('testpass123')
    )
    db_session.add(user)
    db_session.commit()

    # Log in the user
    login_user(auth_client, 'testuser8', 'testpass123')

    # Mock Google Books API response
    mock_response = {
        'items': [{
            'id': 'test123',
            'volumeInfo': {
                'title': '[TEST] Python Programming',
                'authors': ['Test Author'],
                'publishedDate': '2024',
                'description': 'A test book about Python',
                'pageCount': 200,
                'categories': ['Computers', 'Programming'],
                'imageLinks': {
                    'thumbnail': 'https://example.com/thumb.jpg'
                }
            }
        }],
        'totalItems': 1
    }
    
    with patch('routes.books.build') as mock_build:
        # Configure mock
        mock_service = mock_build.return_value
        mock_volumes = mock_service.volumes.return_value
        mock_list = mock_volumes.list.return_value
        mock_list.execute.return_value = mock_response
        
        # Test search
        response = auth_client.get('/books/search')
        csrf_token = get_csrf_token(response)

        response = auth_client.post('/books/search', data={
            'csrf_token': csrf_token,
            'query': 'python'
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'[TEST] Python Programming' in response.data
        assert b'Test Author' in response.data

@patch('extensions.limiter.enabled', False)  # Disable rate limiting for tests
def test_book_search_no_results(auth_client, db_session):
    """Test book search with no results"""
    # Create test user
    user = User(
        username='testuser9',
        email='test9@example.com',
        password=generate_password_hash('testpass123')
    )
    db_session.add(user)
    db_session.commit()

    # Log in the user
    login_user(auth_client, 'testuser9', 'testpass123')

    # Mock empty response
    mock_response = {
        'items': [],
        'totalItems': 0
    }
    
    with patch('routes.books.build') as mock_build:
        # Configure mock
        mock_service = mock_build.return_value
        mock_volumes = mock_service.volumes.return_value
        mock_list = mock_volumes.list.return_value
        mock_list.execute.return_value = mock_response
        
        # Test search
        response = auth_client.get('/books/search')
        csrf_token = get_csrf_token(response)

        response = auth_client.post('/books/search', data={
            'csrf_token': csrf_token,
            'query': 'nonexistentbook123'
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'No books found' in response.data

@patch('extensions.limiter.enabled', False)  # Disable rate limiting for tests
def test_book_search_api_error(auth_client, db_session):
    """Test book search with API error"""
    # Create test user
    user = User(
        username='testuser10',
        email='test10@example.com',
        password=generate_password_hash('testpass123')
    )
    db_session.add(user)
    db_session.commit()

    # Log in the user
    login_user(auth_client, 'testuser10', 'testpass123')

    with patch('routes.books.build') as mock_build:
        # Configure mock to raise an exception
        mock_service = mock_build.return_value
        mock_volumes = mock_service.volumes.return_value
        mock_list = mock_volumes.list.return_value
        mock_list.execute.side_effect = Exception('API Error')
        
        # Test search
        response = auth_client.get('/books/search')
        csrf_token = get_csrf_token(response)

        response = auth_client.post('/books/search', data={
            'csrf_token': csrf_token,
            'query': 'python'
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Error searching books' in response.data