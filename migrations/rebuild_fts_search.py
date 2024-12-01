from sqlalchemy import create_engine, text
from helper import get_database_url
import os

def rebuild_fts_table():
    """Rebuild FTS5 virtual table for book search"""
    engine = create_engine(get_database_url())
    
    with engine.connect() as conn:
        # Drop existing FTS table and triggers
        conn.execute(text("DROP TRIGGER IF EXISTS books_ai"))
        conn.execute(text("DROP TRIGGER IF EXISTS books_au"))
        conn.execute(text("DROP TRIGGER IF EXISTS books_ad"))
        conn.execute(text("DROP TABLE IF EXISTS books_fts"))
        
        # Create FTS5 virtual table with enhanced configuration
        conn.execute(text("""
            CREATE VIRTUAL TABLE books_fts USING fts5(
                title, 
                authors, 
                description, 
                categories,
                publisher,
                tokenize='porter unicode61 remove_diacritics 1',
                prefix='1 2 3',
                content=''
            );
        """))
        
        # Create enhanced triggers that handle NULL values and special characters
        conn.execute(text("""
            CREATE TRIGGER books_ai AFTER INSERT ON books BEGIN
                INSERT INTO books_fts(
                    rowid, 
                    title, 
                    authors, 
                    description, 
                    categories, 
                    publisher
                ) VALUES (
                    new.id, 
                    COALESCE(new.title, ''),
                    COALESCE(new.authors, ''),
                    COALESCE(new.description, ''),
                    COALESCE(new.categories, ''),
                    COALESCE(new.publisher, '')
                );
            END;
        """))
        
        conn.execute(text("""
            CREATE TRIGGER books_au AFTER UPDATE ON books BEGIN
                INSERT INTO books_fts(
                    books_fts,
                    rowid, 
                    title, 
                    authors, 
                    description, 
                    categories, 
                    publisher
                ) VALUES(
                    'delete',
                    old.id,
                    '',
                    '',
                    '',
                    '',
                    ''
                );
                INSERT INTO books_fts(
                    rowid, 
                    title, 
                    authors, 
                    description, 
                    categories, 
                    publisher
                ) VALUES (
                    new.id,
                    COALESCE(new.title, ''),
                    COALESCE(new.authors, ''),
                    COALESCE(new.description, ''),
                    COALESCE(new.categories, ''),
                    COALESCE(new.publisher, '')
                );
            END;
        """))
        
        conn.execute(text("""
            CREATE TRIGGER books_ad AFTER DELETE ON books BEGIN
                INSERT INTO books_fts(books_fts, rowid) VALUES('delete', old.id);
            END;
        """))
        
        # Populate FTS table with existing data
        conn.execute(text("""
            INSERT INTO books_fts(rowid, title, authors, description, categories, publisher)
            SELECT 
                id,
                COALESCE(TRIM(title), ''),
                COALESCE(TRIM(authors), ''),
                COALESCE(TRIM(description), ''),
                COALESCE(TRIM(categories), ''),
                COALESCE(TRIM(publisher), '')
            FROM books;
        """))
        
        conn.commit()
        
        # Verify the rebuild
        count = conn.execute(text("SELECT COUNT(*) FROM books_fts")).scalar()
        print(f"Reindexed {count} books in FTS table")
        
        # Debug: Show some test entries
        print("\nVerifying test entries:")
        test_entries = conn.execute(text("""
            SELECT b.title, f.title as fts_title 
            FROM books b 
            JOIN books_fts f ON b.id = f.rowid 
            WHERE b.title LIKE '[TEST]%' 
            LIMIT 5
        """)).fetchall()
        
        for entry in test_entries:
            print(f"Book: {entry[0]}")
            print(f"FTS:  {entry[1]}\n")

if __name__ == "__main__":
    rebuild_fts_table() 