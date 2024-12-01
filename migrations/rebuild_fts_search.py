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
        
        # Create FTS5 virtual table
        conn.execute(text("""
            CREATE VIRTUAL TABLE books_fts USING fts5(
                title, 
                authors, 
                description, 
                categories,
                publisher,
                tokenize='porter unicode61 remove_diacritics 1'
            );
        """))
        
        # Populate FTS table with existing data
        conn.execute(text("""
            INSERT INTO books_fts(
                rowid, 
                title, 
                authors, 
                description, 
                categories,
                publisher
            )
            SELECT 
                id,
                title,
                authors,
                COALESCE(description, ''),
                COALESCE(categories, ''),
                COALESCE(publisher, '')
            FROM books 
            WHERE title IS NOT NULL AND authors IS NOT NULL;
        """))
        
        conn.commit()
        
        # Debug: Show sample data
        print("\nVerifying FTS content:")
        sample = conn.execute(text("""
            SELECT 
                b.title,
                f.title as fts_title,
                f.authors as fts_authors,
                f.description as fts_desc
            FROM books b 
            JOIN books_fts f ON b.id = f.rowid 
            LIMIT 1
        """)).fetchone()
        
        if sample:
            print("Sample book:")
            print(f"Original title: {sample[0]}")
            print(f"FTS title: {sample[1]}")
            print(f"FTS authors: {sample[2]}")
            print(f"FTS description: {sample[3][:100]}...")
        else:
            print("No books found in FTS table")

if __name__ == "__main__":
    rebuild_fts_table() 