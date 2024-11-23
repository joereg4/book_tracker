from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Book

# Database setup
engine = create_engine('sqlite:///books.db')
Session = sessionmaker(bind=engine)
session = Session()

def clear_google_data(book_id):
    book = session.query(Book).filter_by(id=book_id).first()
    if book:
        book.google_books_id = None
        book.etag = None
        book.self_link = None
        book.publisher = None
        book.description = None
        book.page_count = None
        book.print_type = None
        book.categories = None
        book.maturity_rating = None
        book.language = None
        book.preview_link = None
        book.info_link = None
        book.canonical_volume_link = None
        book.small_thumbnail = None
        book.thumbnail = None
        book.content_version = None
        book.is_ebook = None
        session.commit()
        print(f"Cleared Google Books data for: {book.title}")
    else:
        print("Book not found")

if __name__ == "__main__":
    book_id = input("Enter book ID to clear Google Books data: ")
    clear_google_data(int(book_id)) 