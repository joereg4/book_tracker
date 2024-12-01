from models import Book
from datetime import datetime

def test_shelf_view_empty(client, db_session, app):
    """Test shelf view with empty database"""
    with app.test_request_context():
        response = client.get('/shelf/to_read')
        assert response.status_code == 200
        assert b'To Read' in response.data
        
        response = client.get('/shelf/reading')
        assert response.status_code == 200
        assert b'Currently Reading' in response.data
        
        response = client.get('/shelf/read')
        assert response.status_code == 200
        assert b'Read' in response.data

def test_shelf_view_with_books(client, db_session, app):
    """Test shelf view with sample books"""
    with app.test_request_context():
        # Create test books
        books = [
            Book(
                title='[TEST] Book 1',
                authors='Author 1',
                google_books_id='test1',
                status='to_read',
                description='Test description 1'
            ),
            Book(
                title='[TEST] Book 2',
                authors='Author 2',
                google_books_id='test2',
                status='reading',
                page_count=200
            ),
            Book(
                title='[TEST] Book 3',
                authors='Author 3',
                google_books_id='test3',
                status='read',
                date_read=datetime(2024, 1, 1)
            )
        ]
        
        for book in books:
            db_session.add(book)
        db_session.commit()

        # Test to_read shelf
        response = client.get('/shelf/to_read')
        assert response.status_code == 200
        assert b'[TEST] Book 1' in response.data
        assert b'Author 1' in response.data
        assert b'Test description 1' in response.data
        assert b'[TEST] Book 2' not in response.data
        assert b'[TEST] Book 3' not in response.data

        # Test reading shelf
        response = client.get('/shelf/reading')
        assert response.status_code == 200
        assert b'[TEST] Book 2' in response.data
        assert b'Author 2' in response.data
        assert b'200 pages' in response.data
        assert b'[TEST] Book 1' not in response.data
        assert b'[TEST] Book 3' not in response.data

        # Test read shelf
        response = client.get('/shelf/read')
        assert response.status_code == 200
        assert b'[TEST] Book 3' in response.data
        assert b'Author 3' in response.data
        assert b'January 01, 2024' in response.data
        assert b'[TEST] Book 1' not in response.data
        assert b'[TEST] Book 2' not in response.data

def test_shelf_search(client, db_session, app):
    """Test shelf search functionality"""
    with app.test_request_context():
        # Create test books
        books = [
            Book(
                title='[TEST] Fantasy Book',
                authors='Author 1',
                google_books_id='test1',
                status='read',
                description='A fantasy story'
            ),
            Book(
                title='[TEST] Science Book',
                authors='Author 2',
                google_books_id='test2',
                status='read',
                description='A science story'
            ),
            Book(
                title='[TEST] Historical Fiction',
                authors='Author 3',
                google_books_id='test3',
                status='read',
                description='A story about history'
            )
        ]
        
        for book in books:
            db_session.add(book)
        db_session.commit()

        # Test full word search
        response = client.get('/shelf/read?search=Fantasy')
        assert response.status_code == 200
        assert b'[TEST] Fantasy Book' in response.data
        assert b'[TEST] Science Book' not in response.data

        # Test partial word search
        response = client.get('/shelf/read?search=Sci')
        assert response.status_code == 200
        assert b'[TEST] Science Book' in response.data
        assert b'[TEST] Fantasy Book' not in response.data

        # Test search in description
        response = client.get('/shelf/read?search=history')
        assert response.status_code == 200
        assert b'[TEST] Historical Fiction' in response.data
        assert b'[TEST] Fantasy Book' not in response.data

        # Test search with no results
        response = client.get('/shelf/read?search=nonexistent')
        assert response.status_code == 200
        assert b'Found 0 books' in response.data

def test_shelf_search_edge_cases(client, db_session, app):
    with app.test_request_context():
        # Setup test data
        books = [
            Book(title='[TEST] Special Characters', authors='Test Author 1', status='read'),
            Book(title='[TEST] Multiple Words Here', authors='Test Author 2', status='read'),
            Book(title='[TEST] Partially Matching', authors='Test Author 3', status='read'),
            Book(title='[TEST] UPPERCASE text', authors='Test Author 4', status='read'),
            Book(title='[TEST] Non-ASCII éèê', authors='Test Author 5', status='read'),
        ]
        for book in books:
            db_session.add(book)
        db_session.commit()

        # Test cases
        test_cases = [
            ('', 5),  # Empty search should return all
            ('Special Characters', 1),
            ('Multiple Words', 1),
            ('Partial', 1),
            ('UPPERCASE', 1),
            ('éèê', 1),
        ]

        for search_term, expected_count in test_cases:
            response = client.get(f'/shelf/read?search={search_term}')
            assert response.status_code == 200
            # Add assertions to check the response content 

def test_shelf_search_fuzzy(client, db_session, app):
    """Test fuzzy search functionality"""
    with app.test_request_context():
        # Create test book
        book = Book(
            title='[TEST] Monkey Business',
            authors='Test Author',
            google_books_id='test1',
            status='read',
            description='A story about monkeys'
        )
        db_session.add(book)
        db_session.commit()

        # Test variations of the word
        test_cases = [
            'Monkey',    # Exact match
            'Monke',     # Prefix match
            'monkey',    # Case insensitive
            'MONKEY',    # All caps
            'Munkey',    # Common misspelling
        ]

        for search_term in test_cases:
            response = client.get(f'/shelf/read?search={search_term}')
            assert response.status_code == 200
            assert b'[TEST] Monkey Business' in response.data, f"Failed to find book with search term: {search_term}"