import pytest
from flask import url_for
from models import Book
from datetime import datetime
from routes.books import strip_html_tags

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
        book = db_session.query(Book).filter_by(google_books_id='test123').first()
        assert book is not None
        assert book.title == '[TEST] Add Book Function Test'
        assert book.status == 'to_read'

def test_update_status(client, db_session, app):
    """Test updating a book's status"""
    with app.test_request_context():
        # Create test book
        book = Book(
            title='[TEST] Update Status Test Book',
            authors='Test Author',
            google_books_id='test123',
            status='to_read'
        )
        db_session.add(book)
        db_session.commit()
        
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