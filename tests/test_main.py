from datetime import datetime
from models import Book

def test_index_empty(client, db_session, app):
    """Test index view with empty database"""
    with app.test_request_context():
        response = client.get('/')
        assert response.status_code == 200
        
        # Check reading overview counts
        assert b'<span class="badge bg-primary rounded-pill">0</span>' in response.data  # To Read
        assert b'<span class="badge bg-secondary rounded-pill">0</span>' in response.data  # Reading
        assert b'<span class="badge bg-success rounded-pill">0</span>' in response.data  # Completed
        
        # Check empty states
        assert b'No books currently being read' in response.data
        assert b'Start Reading Something' in response.data

def test_index_with_books(client, db_session, app):
    """Test index view with sample books"""
    with app.test_request_context():
        # Create test books
        books = [
            Book(
                title='[TEST] Reading Book',
                authors='Author 1',
                google_books_id='test1',
                status='reading',
                thumbnail='http://example.com/thumb1.jpg'
            ),
            Book(
                title='[TEST] To Read Book 1',
                authors='Author 2',
                google_books_id='test2',
                status='to_read',
                created_at=datetime(2024, 1, 1)
            ),
            Book(
                title='[TEST] To Read Book 2',
                authors='Author 3',
                google_books_id='test3',
                status='to_read',
                created_at=datetime(2024, 1, 2)
            ),
            Book(
                title='[TEST] Read Book',
                authors='Author 4',
                google_books_id='test4',
                status='read',
                date_read=datetime(2024, 1, 1)
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
        assert b'<span class="badge bg-success rounded-pill">1</span>' in response.data  # Completed
        
        # Check currently reading section
        assert b'[TEST] Reading Book' in response.data
        assert b'Author 1' in response.data
        assert b'Mark as Complete' in response.data
        
        # Check recently added section (should show to_read books)
        assert b'[TEST] To Read Book 1' in response.data
        assert b'[TEST] To Read Book 2' in response.data
        assert b'Start Reading' in response.data
        
        # Check quick actions
        assert b'Reading List' in response.data
        assert b'Completed Books' in response.data
        assert b'View Statistics' in response.data 