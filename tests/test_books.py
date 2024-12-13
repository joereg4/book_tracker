from models import User, Book
from routes.books import strip_html_tags
from werkzeug.security import generate_password_hash

def test_strip_html_tags():
    """Test HTML tag stripping function"""
    # Test basic HTML removal
    assert strip_html_tags('<p>Hello</p>') == 'Hello'
    assert strip_html_tags('<b>Bold</b> text') == 'Bold text'
    
    # Test nested tags
    assert strip_html_tags('<div><p>Nested</p></div>') == 'Nested'
    
    # Test HTML entities
    assert strip_html_tags('&quot;quoted&quot;') == '"quoted"'
    assert strip_html_tags('&amp; and &lt;') == '& and <'
    
    # Test bold tag preservation
    assert strip_html_tags('Text with <b>bold</b> content') == 'Text with bold content'
    assert strip_html_tags('Text with <strong>strong</strong> content') == 'Text with strong content'
    
    # Test empty or None input
    assert strip_html_tags('') == ''
    assert strip_html_tags(None) == ''
    
    # Test multiple spaces
    assert strip_html_tags('Multiple     spaces') == 'Multiple spaces'

def test_add_book(client, db_session, app):
    """Test adding a book"""
    with app.test_request_context():
        # Create and login a test user first
        user = User(
            username='testuser',
            email='test@example.com',
            password=generate_password_hash('testpass')
        )
        db_session.add(user)
        db_session.commit()

        # Login the user
        client.post('/login', data={
            'username': 'testuser',
            'password': 'testpass'
        }, follow_redirects=True)

        # Now try to add the book
        book_data = {
            'id': 'test123',
            'title': '[TEST] Add Book Function Test',
            'authors': 'Test Author',
            'status': 'to_read',
            'published_date': '2023',
            'description': 'Test description'
        }
        
        response = client.post('/books/add', data=book_data)
        assert response.status_code == 302  # Redirect after successful add
        
        # Verify book was added to database
        book = db_session.query(Book).filter_by(google_books_id='test123', user_id=user.id).first()
        assert book is not None
        assert book.title == '[TEST] Add Book Function Test'
        assert book.status == 'to_read'
        assert book.user_id == user.id  # Verify the user_id was set correctly

def test_update_status(client, db_session, app):
    """Test updating a book's status"""
    with app.test_request_context():
        # Create and login test user
        user = User(
            username='testuser',
            email='test@example.com',
            password=generate_password_hash('testpass')
        )
        db_session.add(user)
        db_session.commit()

        # Create test book with user_id
        book = Book(
            title='[TEST] Update Status Test Book',
            authors='Test Author',
            google_books_id='test123',
            status='to_read',
            user_id=user.id
        )
        db_session.add(book)
        db_session.commit()

        # Login user
        client.post('/login', data={
            'username': 'testuser',
            'password': 'testpass'
        }, follow_redirects=True)

        # Update status
        response = client.post(f'/books/update_status/{book.id}', 
                             data={'status': 'read'})
        assert response.status_code == 302
        
        # Refresh the session to see the latest changes
        db_session.expire_all()
        updated_book = db_session.get(Book, book.id)
        assert updated_book.status == 'read'
        assert updated_book.date_read is not None

def test_book_detail(client, db_session, app):
    """Test book detail view"""
    with app.test_request_context():
        # Create test book
        book = Book(
            title='[TEST] Book Detail View Test',
            authors='Test Author',
            google_books_id='test123',
            status='to_read'
        )
        db_session.add(book)
        db_session.commit()
        
        response = client.get(f'/books/book/{book.id}')
        assert response.status_code == 200
        assert b'[TEST] Book Detail View Test' in response.data
        assert b'Test Author' in response.data 