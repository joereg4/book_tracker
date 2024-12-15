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

        with client:
            # Get CSRF token for login
            response = client.get('/login')
            csrf_token = response.data.decode().split('name="csrf_token" value="')[1].split('"')[0]

            # Login the user
            client.post('/login', data={
                'username': 'testuser',
                'password': 'testpass',
                'csrf_token': csrf_token
            }, follow_redirects=True)

            # Get CSRF token for book addition
            response = client.get('/books/search', query_string={'q': 'test'})
            csrf_token = response.data.decode().split('name="csrf_token" value="')[1].split('"')[0]

            # Now try to add the book
            book_data = {
                'id': 'test123',
                'title': '[TEST] Add Book Function Test',
                'authors': 'Test Author',
                'status': 'to_read',
                'published_date': '2023',
                'description': 'Test description',
                'csrf_token': csrf_token
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

        with client:
            # Get CSRF token for login
            response = client.get('/login')
            csrf_token = response.data.decode().split('name="csrf_token" value="')[1].split('"')[0]

            # Login user
            client.post('/login', data={
                'username': 'testuser',
                'password': 'testpass',
                'csrf_token': csrf_token
            }, follow_redirects=True)

            # Get CSRF token for status update
            response = client.get(f'/books/book/{book.id}')
            csrf_token = response.data.decode().split('name="csrf_token" value="')[1].split('"')[0]

            # Update status
            response = client.post(f'/books/update_status/{book.id}', 
                                data={
                                    'status': 'read',
                                    'csrf_token': csrf_token
                                })
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

def test_update_status_without_csrf(client, db_session, app):
    """Test updating a book's status without CSRF token should fail"""
    with app.test_request_context():
        # Create and login test user
        user = User(
            username='testuser',
            email='test@example.com',
            password=generate_password_hash('testpass')
        )
        db_session.add(user)
        db_session.commit()

        # Create test book
        book = Book(
            title='[TEST] CSRF Test Book',
            authors='Test Author',
            google_books_id='test123',
            status='to_read',
            user_id=user.id
        )
        db_session.add(book)
        db_session.commit()

        with client:
            # Login user
            response = client.get('/login')
            csrf_token = response.data.decode().split('name="csrf_token" value="')[1].split('"')[0]
            client.post('/login', data={
                'username': 'testuser',
                'password': 'testpass',
                'csrf_token': csrf_token
            }, follow_redirects=True)

            # Try to update status without CSRF token
            response = client.post(f'/books/update_status/{book.id}', data={
                'status': 'read'
            })
            assert response.status_code == 400  # Should fail with Bad Request
            
            # Verify book status hasn't changed
            db_session.expire_all()
            book = db_session.get(Book, book.id)
            assert book.status == 'to_read'

def test_update_status_with_invalid_csrf(client, db_session, app):
    """Test updating a book's status with invalid CSRF token should fail"""
    with app.test_request_context():
        # Create and login test user
        user = User(
            username='testuser',
            email='test@example.com',
            password=generate_password_hash('testpass')
        )
        db_session.add(user)
        db_session.commit()

        # Create test book
        book = Book(
            title='[TEST] CSRF Test Book',
            authors='Test Author',
            google_books_id='test123',
            status='to_read',
            user_id=user.id
        )
        db_session.add(book)
        db_session.commit()

        with client:
            # Login user
            response = client.get('/login')
            csrf_token = response.data.decode().split('name="csrf_token" value="')[1].split('"')[0]
            client.post('/login', data={
                'username': 'testuser',
                'password': 'testpass',
                'csrf_token': csrf_token
            }, follow_redirects=True)

            # Try to update status with invalid CSRF token
            response = client.post(f'/books/update_status/{book.id}', data={
                'status': 'read',
                'csrf_token': 'invalid_token'
            })
            assert response.status_code == 400  # Should fail with Bad Request
            
            # Verify book status hasn't changed
            db_session.expire_all()
            book = db_session.get(Book, book.id)
            assert book.status == 'to_read'

def test_update_status_all_transitions(client, db_session, app):
    """Test all possible status transitions with proper CSRF tokens"""
    with app.test_request_context():
        # Create and login test user
        user = User(
            username='testuser',
            email='test@example.com',
            password=generate_password_hash('testpass')
        )
        db_session.add(user)
        db_session.commit()

        # Create test book
        book = Book(
            title='[TEST] Status Transition Test Book',
            authors='Test Author',
            google_books_id='test123',
            status='to_read',
            user_id=user.id
        )
        db_session.add(book)
        db_session.commit()

        with client:
            # Login user
            response = client.get('/login')
            csrf_token = response.data.decode().split('name="csrf_token" value="')[1].split('"')[0]
            client.post('/login', data={
                'username': 'testuser',
                'password': 'testpass',
                'csrf_token': csrf_token
            }, follow_redirects=True)

            # Test all status transitions
            transitions = [
                ('to_read', 'reading'),
                ('reading', 'read'),
                ('read', 'to_read'),
                ('to_read', 'read'),
                ('read', 'reading')
            ]

            for old_status, new_status in transitions:
                # Get fresh CSRF token for each request
                response = client.get(f'/books/book/{book.id}')
                csrf_token = response.data.decode().split('name="csrf_token" value="')[1].split('"')[0]

                # Update status
                response = client.post(f'/books/update_status/{book.id}', data={
                    'status': new_status,
                    'csrf_token': csrf_token
                }, follow_redirects=True)
                assert response.status_code == 200

                # Verify status changed
                db_session.expire_all()
                book = db_session.get(Book, book.id)
                assert book.status == new_status

                # Verify date_read is set only when status is 'read'
                if new_status == 'read':
                    assert book.date_read is not None
                elif old_status == 'read' and new_status != 'read':
                    assert book.date_read is not None  # Date should persist

def test_update_status_remove_book(client, db_session, app):
    """Test removing a book through status update"""
    with app.test_request_context():
        # Create and login test user
        user = User(
            username='testuser',
            email='test@example.com',
            password=generate_password_hash('testpass')
        )
        db_session.add(user)
        db_session.commit()

        # Create test book
        book = Book(
            title='[TEST] Remove Book Test',
            authors='Test Author',
            google_books_id='test123',
            status='to_read',
            user_id=user.id
        )
        db_session.add(book)
        db_session.commit()
        book_id = book.id

        with client:
            # Login user
            response = client.get('/login')
            csrf_token = response.data.decode().split('name="csrf_token" value="')[1].split('"')[0]
            client.post('/login', data={
                'username': 'testuser',
                'password': 'testpass',
                'csrf_token': csrf_token
            }, follow_redirects=True)

            # Get fresh CSRF token
            response = client.get(f'/books/book/{book.id}')
            csrf_token = response.data.decode().split('name="csrf_token" value="')[1].split('"')[0]

            # Remove book
            response = client.post(f'/books/update_status/{book.id}', data={
                'status': 'remove',
                'csrf_token': csrf_token
            }, follow_redirects=True)
            assert response.status_code == 200

            # Verify book was deleted
            book = db_session.get(Book, book_id)
            assert book is None