from flask import Flask, render_template, request, redirect, url_for, flash
from olclient import OpenLibrary
from sqlalchemy import create_engine, func, desc, extract
from sqlalchemy.orm import sessionmaker
from models import Base, Book
import os
import requests
import json
from dotenv import load_dotenv
from googleapiclient.discovery import build
from datetime import datetime
import re
from collections import Counter

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your_secret_key')

# Add max and min functions to Jinja environment
app.jinja_env.globals.update(max=max, min=min)

# Database setup
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///books.db')
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)

# Initialize OpenLibrary client
ol = OpenLibrary()

# Load environment variables
load_dotenv()
GOOGLE_BOOKS_API_KEY = os.getenv('GOOGLE_BOOKS_API_KEY')

def strip_html_tags(text):
    """Remove HTML tags from a string"""
    if not text:
        return ''
    clean = re.compile('<.*?>')
    return re.sub(clean, '\n', text).replace('\n\n', '\n').strip()

@app.route('/')
def index():
    """Show dashboard view"""
    db = SessionLocal()
    try:
        to_read = db.query(Book).filter_by(status='to_read')\
                   .order_by(Book.created_at.desc()).all()
        reading = db.query(Book).filter_by(status='reading')\
                   .order_by(Book.created_at.desc()).all()
        read = db.query(Book).filter_by(status='read')\
                .order_by(Book.date_read.desc().nulls_last()).all()
        
        return render_template('index.html', 
                             to_read=to_read,
                             reading=reading,
                             read=read)
    finally:
        db.close()

@app.route('/search', methods=['GET', 'POST'])
def search():
    """Search for books using Google Books API"""
    query = request.form.get('query') or request.args.get('query')
    page = request.args.get('page', 1, type=int)
    results_per_page = 40
    
    if not query:
        return render_template('search.html', results_per_page=results_per_page)
    
    try:
        if not GOOGLE_BOOKS_API_KEY:
            flash('API key not found', 'error')
            return render_template('search.html', results_per_page=results_per_page)
        
        # Get existing books from database for comparison
        db = SessionLocal()
        existing_books = {book.google_books_id: book.status 
                         for book in db.query(Book).all()}
        
        # Clean up the query if it's a subject search
        if query.startswith('subject:'):
            # Remove quotes if they exist and ensure proper format
            category = query.replace('subject:', '').strip('"\'')
            query = f'subject:"{category}"'
        
        service = build('books', 'v1', developerKey=GOOGLE_BOOKS_API_KEY)
        result = service.volumes().list(
            q=query,
            startIndex=((page - 1) * results_per_page),
            maxResults=results_per_page,
            orderBy='relevance'
        ).execute()
        
        total_items = result.get('totalItems', 0)
        total_pages = (total_items + results_per_page - 1) // results_per_page
        
        books = []
        if 'items' in result:
            for item in result['items']:
                volume_info = item.get('volumeInfo', {})
                image_links = volume_info.get('imageLinks', {})
                
                # Check if book already exists in database
                existing_status = existing_books.get(item['id'])
                
                book = {
                    'id': item['id'],
                    'title': volume_info.get('title', 'Unknown Title'),
                    'authors': volume_info.get('authors', ['Unknown Author']),
                    'published_date': volume_info.get('publishedDate', ''),
                    'description': strip_html_tags(volume_info.get('description', '')),
                    'page_count': volume_info.get('pageCount'),
                    'categories': volume_info.get('categories', []),
                    'language': volume_info.get('language'),
                    'publisher': volume_info.get('publisher'),
                    'thumbnail': image_links.get('thumbnail', ''),
                    'small_thumbnail': image_links.get('smallThumbnail', ''),
                    'isbn': next((i['identifier'] for i in volume_info.get('industryIdentifiers', []) 
                                if i['type'] == 'ISBN_10'), ''),
                    'isbn13': next((i['identifier'] for i in volume_info.get('industryIdentifiers', []) 
                                  if i['type'] == 'ISBN_13'), ''),
                    'etag': item.get('etag', ''),
                    'self_link': item.get('selfLink', ''),
                    'print_type': volume_info.get('printType', ''),
                    'maturity_rating': volume_info.get('maturityRating', ''),
                    'preview_link': volume_info.get('previewLink', ''),
                    'info_link': volume_info.get('infoLink', ''),
                    'canonical_volume_link': volume_info.get('canonicalVolumeLink', ''),
                    'content_version': volume_info.get('contentVersion', ''),
                    'is_ebook': item.get('saleInfo', {}).get('isEbook', False),
                    'existing_status': existing_books.get(item['id'])
                }
                books.append(book)
        
        return render_template('search.html', 
                             results=books, 
                             query=query,
                             page=page,
                             total_pages=total_pages,
                             total_items=total_items,
                             results_per_page=results_per_page)
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        flash(f'Error searching books: {str(e)}', 'error')
        return render_template('search.html', results_per_page=results_per_page)
    finally:
        if 'db' in locals():
            db.close()

@app.route('/add_book', methods=['POST'])
def add_book():
    db = SessionLocal()
    try:
        # Check if book already exists
        google_books_id = request.form.get('id')
        existing_book = db.query(Book).filter_by(google_books_id=google_books_id).first()
        
        if existing_book:
            flash('Book already exists in your library', 'warning')
            return redirect(url_for('index'))
        
        # Create new book with all fields from the form
        new_book = Book(
            google_books_id=google_books_id,
            title=request.form.get('title'),
            authors=request.form.get('authors'),
            status=request.form.get('status', 'to_read'),
            published_date=request.form.get('published_date'),
            description=request.form.get('description'),
            page_count=request.form.get('page_count'),
            categories=request.form.get('categories'),
            language=request.form.get('language'),
            publisher=request.form.get('publisher'),
            isbn=request.form.get('isbn'),
            isbn13=request.form.get('isbn13'),
            thumbnail=request.form.get('thumbnail'),
            small_thumbnail=request.form.get('small_thumbnail'),
            # Add all Google Books specific fields
            etag=request.form.get('etag'),
            self_link=request.form.get('self_link'),
            print_type=request.form.get('print_type'),
            maturity_rating=request.form.get('maturity_rating'),
            preview_link=request.form.get('preview_link'),
            info_link=request.form.get('info_link'),
            canonical_volume_link=request.form.get('canonical_volume_link'),
            content_version=request.form.get('content_version'),
            is_ebook=request.form.get('is_ebook') == 'true'
        )
        
        if new_book.status == 'read':
            new_book.date_read = datetime.now()
            
        db.add(new_book)
        db.commit()
        flash('Book added successfully!', 'success')
        
    except Exception as e:
        db.rollback()
        flash(f'Error adding book: {str(e)}', 'error')
    finally:
        db.close()
    
    return redirect(url_for('index'))

@app.route('/shelf/<shelf>')
def shelf_view(shelf):
    """Display books on a specific shelf"""
    titles = {
        'to_read': 'To Read',
        'reading': 'Currently Reading',
        'read': 'Read'
    }
    
    db = SessionLocal()
    try:
        # Different ordering based on shelf
        if shelf == 'read':
            # Order read books by date_read (newest first), then created_at for books without date_read
            books = db.query(Book).filter_by(status=shelf)\
                     .order_by(Book.date_read.desc().nulls_last(),
                              Book.created_at.desc()).all()
        else:
            # Other shelves ordered by created date
            books = db.query(Book).filter_by(status=shelf)\
                     .order_by(Book.created_at.desc()).all()
            
        return render_template('shelf.html',
                             books=books,
                             title=titles.get(shelf, 'Books'),
                             current_shelf=shelf)
    finally:
        db.close()

@app.route('/stats')
def stats():
    db = SessionLocal()
    try:
        # Get selected year from query params
        selected_year = request.args.get('year', type=int)
        
        # Calculate overall stats
        total_books = db.query(Book).count()
        current_year = datetime.now().year
        books_this_year = db.query(Book)\
            .filter(Book.date_read.isnot(None))\
            .filter(extract('year', Book.date_read) == current_year)\
            .count()
        
        # Calculate total pages
        total_pages = db.query(func.sum(Book.page_count))\
            .filter(Book.status == 'read')\
            .scalar() or 0
            
        # Get books by year read (instead of publication year)
        years = db.query(
            extract('year', Book.date_read).label('year'),
            func.count().label('count')
        ).filter(Book.status == 'read')\
         .filter(Book.date_read.isnot(None))\
         .group_by('year')\
         .order_by(desc('year'))\
         .all()
        
        # Get books for selected year
        books = None
        if selected_year:
            books = db.query(Book)\
                .filter(Book.status == 'read')\
                .filter(extract('year', Book.date_read) == selected_year)\
                .order_by(Book.date_read.desc())\
                .all()

        # Get categories and their counts
        categories = []
        for book in db.query(Book).all():
            if book.categories:
                cats = [c.strip() for c in book.categories.split(',')]
                categories.extend(cats)
        
        category_counts = Counter(categories)
        top_categories = category_counts.most_common(15)  # Get top 15 categories
        max_category_count = max(count for _, count in top_categories) if top_categories else 1
        
        # Get most read publisher
        most_read_publisher = db.query(
            Book.publisher,
            func.count().label('count')
        ).filter(Book.publisher.isnot(None))\
         .group_by(Book.publisher)\
         .order_by(desc('count'))\
         .first()
        
        # Get most read author
        most_read_author = db.query(
            Book.authors,
            func.count().label('count')
        ).group_by(Book.authors)\
         .order_by(desc('count'))\
         .first()
        
        # Calculate average pages per book
        avg_pages = db.query(func.avg(Book.page_count))\
            .filter(Book.page_count.isnot(None))\
            .scalar() or 0
        
        return render_template('stats.html',
                             total_books=total_books,
                             books_this_year=books_this_year,
                             total_pages=total_pages,
                             years=years,
                             selected_year=selected_year,
                             books=books,
                             top_categories=top_categories,
                             max_category_count=max_category_count,
                             most_read_publisher=most_read_publisher[0] if most_read_publisher else "None",
                             most_read_author=most_read_author[0] if most_read_author else "None",
                             avg_pages=avg_pages)
    finally:
        db.close()

@app.route('/book/<book_id>')
def book_detail(book_id):
    """Display details for a specific book"""
    db = SessionLocal()
    try:
        book = db.query(Book).filter_by(id=book_id).first()
        if not book:
            flash('Book not found', 'error')
            return redirect(url_for('index'))
        
        # Get the referrer but exclude the edit page
        referrer = request.referrer
        if referrer and '/edit' not in referrer:
            back_url = referrer
        else:
            # Default to the appropriate shelf view
            back_url = url_for('shelf_view', shelf=book.status)
            
        return render_template('book.html', 
                             book=book,
                             current_shelf=book.status,
                             back_url=back_url)
    finally:
        db.close()

@app.route('/update_status/<book_id>', methods=['POST'])
def update_status(book_id):
    """Update a book's status"""
    new_status = request.form.get('status')
    db = SessionLocal()
    try:
        book = db.query(Book).filter_by(id=book_id).first()
        if not book:
            flash('Book not found', 'error')
            return redirect(url_for('index'))
            
        if new_status == 'remove':
            db.delete(book)
            flash('Book removed from your library', 'success')
        else:
            book.status = new_status
            if new_status == 'read':
                book.date_read = datetime.now()
            flash(f'Book moved to "{new_status}" shelf', 'success')
            
        db.commit()
    except Exception as e:
        db.rollback()
        flash(f'Error updating book status: {str(e)}', 'error')
    finally:
        db.close()
    return redirect(request.referrer or url_for('index'))

@app.route('/book/<book_id>/edit', methods=['GET', 'POST'])
def edit_book(book_id):
    db = SessionLocal()
    try:
        book = db.query(Book).filter_by(id=book_id).first()
        if not book:
            flash('Book not found', 'error')
            return redirect(url_for('index'))

        if request.method == 'POST':
            print("Form data received:", request.form)  # Debug log
            
            if 'cancel' in request.form:
                return redirect(url_for('book_detail', book_id=book_id))

            # Handle Google Books refresh
            should_refresh = 'refresh_google' in request.form
            print("Should refresh:", should_refresh)  # Debug log
            
            if should_refresh:
                print("Starting refresh process")  # Debug log
                google_id = request.form.get('google_books_id') or book.google_books_id
                try:
                    service = build('books', 'v1', developerKey=GOOGLE_BOOKS_API_KEY)
                    result = service.volumes().get(volumeId=google_id).execute()
                    
                    # Extract volume info
                    volume_info = result.get('volumeInfo', {})
                    image_links = volume_info.get('imageLinks', {})
                    
                    # Create preview data without saving
                    preview_data = {
                        'title': volume_info.get('title'),
                        'authors': volume_info.get('authors', []),
                        'published_date': volume_info.get('publishedDate'),
                        'description': strip_html_tags(volume_info.get('description', '')),
                        'page_count': volume_info.get('pageCount'),
                        'categories': volume_info.get('categories', []),
                        'language': volume_info.get('language'),
                        'publisher': volume_info.get('publisher'),
                        'thumbnail': image_links.get('thumbnail'),
                        'small_thumbnail': image_links.get('smallThumbnail'),
                        'isbn': next((i['identifier'] for i in volume_info.get('industryIdentifiers', []) 
                                    if i['type'] == 'ISBN_10'), ''),
                        'isbn13': next((i['identifier'] for i in volume_info.get('industryIdentifiers', []) 
                                      if i['type'] == 'ISBN_13'), ''),
                        'preview_link': volume_info.get('previewLink', ''),
                        'info_link': volume_info.get('infoLink', ''),
                        'canonical_volume_link': volume_info.get('canonicalVolumeLink', ''),
                        'maturity_rating': volume_info.get('maturityRating', ''),
                        'print_type': volume_info.get('printType', ''),
                        'etag': result.get('etag'),
                        'self_link': result.get('selfLink'),
                        'content_version': result.get('volumeInfo', {}).get('contentVersion', ''),
                        'is_ebook': result.get('saleInfo', {}).get('isEbook', False)
                    }
                    
                    # Debug print to see what we're getting from the API
                    print("API Response:", json.dumps(result, indent=2))
                    print("Preview Data:", json.dumps(preview_data, indent=2))
                    
                    # Return the edit template with both current and preview data
                    return render_template('edit_book.html', book=book, preview_data=preview_data)
                    
                except Exception as e:
                    flash(f'Error refreshing book data: {str(e)}', 'error')
                    print(f"Refresh error: {str(e)}")  # Debug log

            # Handle manual field updates
            else:
                # Update all editable fields
                editable_fields = [
                    'title', 'authors', 'published_date', 'description', 'page_count',
                    'publisher', 'isbn', 'isbn13', 'thumbnail', 'etag', 'self_link',
                    'print_type', 'categories', 'maturity_rating', 'language',
                    'preview_link', 'info_link', 'canonical_volume_link',
                    'small_thumbnail', 'content_version', 'is_ebook'
                ]
                
                for field in editable_fields:
                    if value := request.form.get(field):
                        if field == 'is_ebook':
                            setattr(book, field, value.lower() == 'true')
                        else:
                            setattr(book, field, value)

            # Handle date_read for books on 'read' shelf
            if book.status == 'read' and (date_read := request.form.get('date_read')):
                try:
                    book.date_read = datetime.strptime(date_read, '%Y-%m-%d')
                except ValueError:
                    flash('Invalid date format for date read', 'error')

            db.commit()
            flash('Book updated successfully!', 'success')
            return redirect(url_for('book_detail', book_id=book_id))

        return render_template('edit_book.html', book=book)
    finally:
        db.close()

@app.route('/category/<category>')
def category_view(category):
    db = SessionLocal()
    try:
        # Get all books in this category, ordered by read date
        books = db.query(Book)\
            .filter(Book.categories.ilike(f'%{category}%'))\
            .filter(Book.status == 'read')\
            .order_by(Book.date_read.desc())\
            .all()
            
        return render_template('category.html',
                             category=category,
                             books=books)
    finally:
        db.close()

if __name__ == '__main__':
    app.run(debug=True)