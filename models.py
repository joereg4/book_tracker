from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from flask_login import UserMixin

Base = declarative_base()

class Book(Base):
    __tablename__ = 'books'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    title = Column(String, nullable=False)
    authors = Column(String, nullable=False)
    isbn = Column(String)
    isbn13 = Column(String)
    published_date = Column(String)
    status = Column(String, nullable=False, default='to_read')
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    date_read = Column(DateTime, nullable=True)
    google_books_id = Column(String)
    etag = Column(String)
    self_link = Column(String)
    publisher = Column(String)
    description = Column(Text)
    page_count = Column(Integer)
    print_type = Column(String)
    categories = Column(String)
    maturity_rating = Column(String)
    language = Column(String)
    preview_link = Column(String)
    info_link = Column(String)
    canonical_volume_link = Column(String)
    
    small_thumbnail = Column(String)
    thumbnail = Column(String)
    
    content_version = Column(String)
    is_ebook = Column(Boolean)
    
    user = relationship('User', back_populates='books')
    
    def __repr__(self):
        return f"<Book(title='{self.title}', authors='{self.authors}', status='{self.status}')>"
    
    def update_from_google_books(self, item):
        """Update book with data from Google Books API"""
        volume_info = item.get('volumeInfo', {})
        
        # Basic info
        self.google_books_id = item.get('id')
        self.etag = item.get('etag')
        self.self_link = item.get('selfLink')
        
        # Volume info
        if not self.title:
            self.title = volume_info.get('title')
        if not self.authors and 'authors' in volume_info:
            self.authors = ', '.join(volume_info['authors'])
        self.publisher = volume_info.get('publisher')
        self.published_date = volume_info.get('publishedDate')
        self.description = volume_info.get('description')
        self.page_count = volume_info.get('pageCount')
        self.print_type = volume_info.get('printType')
        
        # Categories
        if 'categories' in volume_info:
            self.categories = ','.join(volume_info['categories'])
        
        # Other metadata
        self.maturity_rating = volume_info.get('maturityRating')
        self.language = volume_info.get('language')
        self.preview_link = volume_info.get('previewLink')
        self.info_link = volume_info.get('infoLink')
        self.canonical_volume_link = volume_info.get('canonicalVolumeLink')
        
        # Image links
        image_links = volume_info.get('imageLinks', {})
        self.small_thumbnail = image_links.get('smallThumbnail')
        self.thumbnail = image_links.get('thumbnail')
        
        # ISBN handling
        for identifier in volume_info.get('industryIdentifiers', []):
            if identifier['type'] == 'ISBN_13':
                self.isbn13 = identifier['identifier']
            elif identifier['type'] == 'ISBN_10':
                self.isbn = identifier['identifier']
        
        # Sale info
        sale_info = item.get('saleInfo', {})
        self.is_ebook = sale_info.get('isEbook', False)

class User(Base, UserMixin):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password = Column(String(128), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Direct relationship to books
    books = relationship('Book', back_populates='user')
    
    def __repr__(self):
        return f'<User {self.username}>'
