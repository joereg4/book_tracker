from datetime import datetime
from models import Book
from flask import url_for

def test_dashboard_empty(client, db_session, app):
    """Test stats dashboard with empty database"""
    with app.test_request_context():
        response = client.get('/stats/')
        assert response.status_code == 200
        
        # Verify default values when no books exist
        assert b'<span>Total Books</span>' in response.data
        assert b'<span class="badge bg-primary rounded-pill">0</span>' in response.data
        assert b'<span>Books Read This Year</span>' in response.data
        assert b'<span class="badge bg-success rounded-pill">0</span>' in response.data
        assert b'<span>Total Pages Read</span>' in response.data
        assert b'<span class="badge bg-secondary rounded-pill">0</span>' in response.data

def test_dashboard_with_books(client, db_session, app):
    """Test stats dashboard with sample books"""
    with app.test_request_context():
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
                publisher='Publisher A'
            ),
            Book(
                title='[TEST] Book 2',
                authors='Author 1',  # Same author
                google_books_id='test2',
                status='read',
                date_read=datetime(2023, 12, 1),
                page_count=300,
                categories='Fiction, Science Fiction',
                publisher='Publisher B'
            ),
            Book(
                title='[TEST] Book 3',
                authors='Author 2',
                google_books_id='test3',
                status='to_read',  # Unread book
                page_count=250,
                categories='Non-Fiction',
                publisher='Publisher A'  # Same publisher as Book 1
            )
        ]
        
        for book in books:
            db_session.add(book)
        db_session.commit()

        # Test overall stats
        response = client.get('/stats/')
        assert response.status_code == 200
        
        # Basic stats
        assert b'<span>Total Books</span>' in response.data
        assert b'<span class="badge bg-primary rounded-pill">3</span>' in response.data
        
        current_year = datetime.now().year
        if current_year == 2024:  # Adjust test based on current year
            assert b'<span class="badge bg-success rounded-pill">1</span>' in response.data
        
        # Pages stats
        assert b'<span>Total Pages Read</span>' in response.data
        assert b'<span class="badge bg-secondary rounded-pill">500</span>' in response.data
        assert b'<span class="badge bg-secondary">250</span>' in response.data

        # Test year filtering
        response = client.get('/stats/?year=2024')
        assert response.status_code == 200
        assert b'[TEST] Book 1' in response.data
        
        # Verify that Book 2 doesn't appear in the "Books Read in 2024" section
        assert b'Books Read in 2024' in response.data
        assert b'January 01, 2024' in response.data
        assert b'Read on: December 01, 2023' not in response.data

def test_dashboard_categories(client, db_session, app):
    """Test category statistics"""
    with app.test_request_context():
        # Create test books with categories
        books = [
            Book(
                title='[TEST] Category Book 1',
                authors='Test Author',
                google_books_id='cat1',
                categories='Fiction, Fantasy',
                status='read'
            ),
            Book(
                title='[TEST] Category Book 2',
                authors='Test Author',
                google_books_id='cat2',
                categories='Fiction, Science Fiction',
                status='read'
            ),
            Book(
                title='[TEST] Category Book 3',
                authors='Test Author',
                google_books_id='cat3',
                categories='Fiction',
                status='read'
            )
        ]
        
        for book in books:
            db_session.add(book)
        db_session.commit()

        response = client.get('/stats/')
        assert response.status_code == 200
        
        # Check if categories appear in response
        assert b'Fiction' in response.data
        assert b'Fantasy' in response.data
        assert b'Science Fiction' in response.data 