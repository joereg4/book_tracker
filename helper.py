from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from models import Book, Base

# Configure your database URL
DATABASE_URL = 'sqlite:///books.db'  # Example using SQLite

# Create a new database session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def get_book_status(open_library_id):
    """Check if a book exists in the database and return its status."""
    db = SessionLocal()
    try:
        book = db.query(Book).filter_by(open_library_id=open_library_id).first()
        if book:
            return book.status
        return None
    finally:
        db.close() 