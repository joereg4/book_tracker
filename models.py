from datetime import datetime, timezone, UTC
from flask_login import UserMixin
from extensions import db

class Book(db.Model):
    __tablename__ = 'books'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    title = db.Column(db.String, nullable=False)
    authors = db.Column(db.String, nullable=False)
    isbn = db.Column(db.String)
    isbn13 = db.Column(db.String)
    published_date = db.Column(db.String)
    status = db.Column(db.String, nullable=False, default='to_read')
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    date_read = db.Column(db.DateTime, nullable=True)
    google_books_id = db.Column(db.String)
    etag = db.Column(db.String)
    self_link = db.Column(db.String)
    publisher = db.Column(db.String)
    description = db.Column(db.Text)
    page_count = db.Column(db.Integer)
    print_type = db.Column(db.String)
    categories = db.Column(db.String)
    maturity_rating = db.Column(db.String)
    language = db.Column(db.String)
    preview_link = db.Column(db.String)
    info_link = db.Column(db.String)
    canonical_volume_link = db.Column(db.String)
    
    small_thumbnail = db.Column(db.String)
    thumbnail = db.Column(db.String)
    
    content_version = db.Column(db.String)
    is_ebook = db.Column(db.Boolean)
    
    user = db.relationship('User', back_populates='books')
    
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

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    last_seen = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    reset_token = db.Column(db.String(100), unique=True)
    reset_token_expiry = db.Column(db.DateTime)
    
    books = db.relationship('Book', back_populates='user', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.username}>'
