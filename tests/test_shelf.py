from models import User, Book
from werkzeug.security import generate_password_hash
from datetime import datetime
from sqlalchemy import text
from tests.utils import get_csrf_token, login_user
import json

def test_shelf_view_empty(auth_client):
    """Test shelf view with empty database"""
    # Test each shelf type
    for shelf in ['to_read', 'reading', 'read']:
        response = auth_client.get(f'/shelf/{shelf}')
        assert response.status_code == 200
        assert b'<div class="list-group">\n        \n    </div>' in response.data

def test_shelf_view_with_books(auth_client, db_session):
    """Test shelf view with sample books"""
    # Get the test user
    user = User.query.filter_by(username='testuser').first()
    
    # Create test books
    books = [
        Book(
            title='[TEST] Book 1',
            authors='Author 1',
            google_books_id='test1',
            status='to_read',
            description='Test description 1',
            user_id=user.id
        ),
        Book(
            title='[TEST] Book 2',
            authors='Author 2',
            google_books_id='test2',
            status='reading',
            page_count=200,
            user_id=user.id
        ),
        Book(
            title='[TEST] Book 3',
            authors='Author 3',
            google_books_id='test3',
            status='read',
            date_read=datetime(2024, 1, 1),
            user_id=user.id
        )
    ]

    for book in books:
        db_session.add(book)
    db_session.commit()

    # Test to-read shelf
    response = auth_client.get('/shelf/to_read')
    assert response.status_code == 200
    assert b'[TEST] Book 1' in response.data
    assert b'Author 1' in response.data
    assert b'Test description 1' in response.data

    # Test reading shelf
    response = auth_client.get('/shelf/reading')
    assert response.status_code == 200
    assert b'[TEST] Book 2' in response.data
    assert b'Author 2' in response.data
    assert b'200 pages' in response.data

    # Test read shelf
    response = auth_client.get('/shelf/read')
    assert response.status_code == 200
    assert b'[TEST] Book 3' in response.data
    assert b'Author 3' in response.data
    assert b'January 01, 2024' in response.data

def test_shelf_search(auth_client, db_session):
    """Test shelf search functionality"""
    # Get the test user
    user = User.query.filter_by(username='testuser').first()
    
    # Create FTS table and triggers
    db_session.execute(text("""
        CREATE VIRTUAL TABLE IF NOT EXISTS books_fts USING fts5(
            title,
            authors,
            description,
            categories,
            publisher,
            tokenize='porter unicode61 remove_diacritics 1'
        )
    """))
    
    db_session.execute(text("""
        CREATE TRIGGER IF NOT EXISTS books_ai AFTER INSERT ON books BEGIN
            INSERT INTO books_fts(rowid, title, authors, description, categories, publisher)
            VALUES (new.id, new.title, new.authors, new.description, new.categories, new.publisher);
        END;
    """))
    
    db_session.execute(text("""
        CREATE TRIGGER IF NOT EXISTS books_ad AFTER DELETE ON books BEGIN
            DELETE FROM books_fts WHERE rowid = old.id;
        END;
    """))
    
    db_session.execute(text("""
        CREATE TRIGGER IF NOT EXISTS books_au AFTER UPDATE ON books BEGIN
            DELETE FROM books_fts WHERE rowid = old.id;
            INSERT INTO books_fts(rowid, title, authors, description, categories, publisher)
            VALUES (new.id, new.title, new.authors, new.description, new.categories, new.publisher);
        END;
    """))
    
    # Create test books
    books = [
        Book(
            title='[TEST] Fantasy Book',
            authors='Author 1',
            google_books_id='test1',
            status='read',
            description='A fantasy story',
            user_id=user.id
        ),
        Book(
            title='[TEST] Science Book',
            authors='Author 2',
            google_books_id='test2',
            status='read',
            description='A science story',
            user_id=user.id
        )
    ]

    for book in books:
        db_session.add(book)
    db_session.commit()

    # Re-insert books to trigger FTS indexing
    for book in books:
        db_session.execute(text("""
            UPDATE books SET title = title WHERE id = :id
        """), {'id': book.id})
    db_session.commit()

    # Test search functionality
    response = auth_client.get('/shelf/read?search=fantasy')
    assert response.status_code == 200
    assert b'[TEST] Fantasy Book' in response.data
    assert b'A fantasy story' in response.data
    assert b'[TEST] Science Book' not in response.data

    # Test search for science book
    response = auth_client.get('/shelf/read?search=science')
    assert response.status_code == 200
    assert b'[TEST] Science Book' in response.data
    assert b'A science story' in response.data
    assert b'[TEST] Fantasy Book' not in response.data