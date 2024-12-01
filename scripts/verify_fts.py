from sqlalchemy import create_engine, text
from helper import get_database_url
import os

def verify_fts_setup():
    """Verify FTS5 virtual table setup and functionality"""
    engine = create_engine(get_database_url())
    
    with engine.connect() as conn:
        print("\n=== FTS Setup Verification ===\n")
        
        # Check if FTS table exists
        try:
            result = conn.execute(text("SELECT * FROM books_fts WHERE 0"))
            print("✅ FTS table exists")
        except Exception as e:
            print("❌ FTS table does not exist:", str(e))
            return
        
        # Check if triggers exist
        triggers = ['books_ai', 'books_au', 'books_ad']
        for trigger in triggers:
            result = conn.execute(text(
                "SELECT sql FROM sqlite_master WHERE type='trigger' AND name=:trigger"
            ), {'trigger': trigger})
            trigger_sql = result.scalar()
            if trigger_sql:
                print(f"✅ Trigger '{trigger}' exists")
                print(f"   SQL: {trigger_sql}")
            else:
                print(f"❌ Trigger '{trigger}' is missing")
        
        # Verify FTS table configuration
        try:
            result = conn.execute(text("SELECT sql FROM sqlite_master WHERE type='table' AND name='books_fts'"))
            fts_sql = result.scalar()
            print("\nFTS Table Definition:")
            print(fts_sql)
            
            if 'tokenize=porter' in fts_sql.lower():
                print("✅ Porter tokenizer is configured")
            else:
                print("❌ Porter tokenizer not found in table definition")
        except Exception as e:
            print("❌ Could not verify FTS configuration:", str(e))
            
        # Count records
        books_count = conn.execute(text("SELECT COUNT(*) FROM books")).scalar()
        fts_count = conn.execute(text("SELECT COUNT(*) FROM books_fts")).scalar()
        
        print(f"\nRecord counts:")
        print(f"Books table: {books_count}")
        print(f"FTS table: {fts_count}")
        
        if books_count == fts_count:
            print("✅ Record counts match")
        else:
            print("❌ Record count mismatch")
        
        print("\n=== Search Tests ===\n")
        
        # First, let's verify the test data is actually in the database
        print("\nVerifying test data:")
        test_books = conn.execute(text("""
            SELECT title FROM books 
            WHERE title LIKE '[TEST]%'
            ORDER BY title
        """)).fetchall()
        
        if test_books:
            print("Found test books in database:")
            for book in test_books:
                print(f"- {book[0]}")
        else:
            print("❌ No test books found in database")
        
        print("\nVerifying FTS index:")
        fts_books = conn.execute(text("""
            SELECT b.title 
            FROM books_fts f
            JOIN books b ON b.id = f.rowid
            WHERE b.title LIKE '[TEST]%'
            ORDER BY b.title
        """)).fetchall()
        
        if fts_books:
            print("Found test books in FTS index:")
            for book in fts_books:
                print(f"- {book[0]}")
        else:
            print("❌ No test books found in FTS index")
        
        test_cases = [
            ("exact title", "[TEST]", "title:TEST"),  # Search without brackets first
            ("special chars", "[TEST]", 'title:"[TEST]"'),  # Then with brackets
            ("partial word", "Sci", "title:Sci*"),
            ("case insensitive", "FANTASY", "title:fantasy"),
            ("multi-word", "Science Book", 'title:"Science Book"'),
            ("description", "story about", 'description:"story about"'),
            ("fuzzy match", "Monkey", "title:monkey OR title:monk*"),
        ]
        
        for test_type, search_term, query_term in test_cases:
            try:
                results = conn.execute(text("""
                    SELECT 
                        b.title,
                        b.authors,
                        SUBSTR(b.description, 1, 100) as description,
                        highlight(books_fts, 0, '[MATCH]', '[/MATCH]') as title_match,
                        highlight(books_fts, 2, '[MATCH]', '[/MATCH]') as desc_match,
                        bm25(books_fts) as rank
                    FROM books_fts
                    JOIN books b ON b.id = books_fts.rowid 
                    WHERE books_fts MATCH :search
                    ORDER BY bm25(books_fts)
                    LIMIT 5
                """), {'search': query_term}).fetchall()
                
                print(f"\nSearch test ({test_type}):")
                print(f"- Term: '{search_term}' (Query: '{query_term}')")
                print(f"- Total Results: {len(results)}")
                
                if results:
                    print("- Matches:")
                    for row in results:
                        print(f"  • Title: {row[0]}")
                        print(f"    Author: {row[1]}")
                        if row[2]:
                            print(f"    Description: {row[2]}...")
                        if row[3] and row[3] != row[0]:
                            print(f"    Title Match: {row[3]}")
                        if row[4]:
                            print(f"    Desc Match: {row[4]}")
                        print(f"    Rank: {row[5]}\n")
                print("✅ Search executed successfully\n")
                
            except Exception as e:
                print(f"❌ Search test failed ({test_type}):", str(e))
                print(f"   Search term: {search_term}")
                print(f"   Query term: {query_term}")
        
        print("=== Verification Complete ===")

if __name__ == "__main__":
    verify_fts_setup() 