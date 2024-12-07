"""Add user authentication and link existing books

This migration:
1. Creates the users table
2. Adds user_id column to books table
3. Creates your user account
4. Links all existing books to your account
"""

from sqlalchemy import create_engine, text
from werkzeug.security import generate_password_hash

def upgrade(db_path):
    """Add users table and link existing books"""
    engine = create_engine(f'sqlite:///{db_path}')
    
    with engine.connect() as conn:
        # Create users table
        conn.execute(text('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(80) NOT NULL UNIQUE,
            email VARCHAR(120) NOT NULL UNIQUE,
            password VARCHAR(128) NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        '''))
        
        # Add user_id to books table
        conn.execute(text('ALTER TABLE books ADD COLUMN user_id INTEGER REFERENCES users(id)'))
        
        # Create your user account
        conn.execute(text('''
        INSERT INTO users (username, email, password)
        VALUES (:username, :email, :password)
        '''), {
            'username': 'joereg4',
            'email': 'joereg4@protonmail.com',  # Replace with your actual email
            'password': generate_password_hash('changeme')  # Change this password after setup
        })
        
        # Link all existing books to your account
        conn.execute(text('UPDATE books SET user_id = 1'))  # 1 will be your user ID
        
        conn.commit()

def downgrade(db_path):
    """Remove user authentication"""
    engine = create_engine(f'sqlite:///{db_path}')
    
    with engine.connect() as conn:
        # Remove user_id from books
        conn.execute(text('''
        CREATE TABLE books_temp AS 
        SELECT id, title, authors, isbn, isbn13, published_date, status,
               created_at, date_read, google_books_id, etag, self_link,
               publisher, description, page_count, print_type, categories,
               maturity_rating, language, preview_link, info_link,
               canonical_volume_link, small_thumbnail, thumbnail,
               content_version, is_ebook
        FROM books
        '''))
        conn.execute(text('DROP TABLE books'))
        conn.execute(text('ALTER TABLE books_temp RENAME TO books'))
        
        # Drop users table
        conn.execute(text('DROP TABLE users'))
        
        conn.commit()