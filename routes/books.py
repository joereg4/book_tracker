from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import datetime
import re
from googleapiclient.discovery import build
import os
from helper import create_session
from models import Book
from flask_login import login_required, current_user

# Initialize blueprint
bp = Blueprint('books', __name__, url_prefix='/books')

# Get API key from environment
GOOGLE_BOOKS_API_KEY = os.getenv('GOOGLE_BOOKS_API_KEY')

def strip_html_tags(text):
    """Remove HTML tags and decode HTML entities from a string"""
    if not text:
        return ''
    
    # First pass: remove bold tags specifically (replace with their content)
    text = re.sub(r'<b>(.*?)</b>', r'\1', text)
    text = re.sub(r'<strong>(.*?)</strong>', r'\1', text)
    
    # Second pass: remove remaining HTML tags
    clean = re.compile('<.*?>')
    text = re.sub(clean, ' ', text)
    
    # Replace common HTML entities
    text = text.replace('&nbsp;', ' ')\
               .replace('&amp;', '&')\
               .replace('&lt;', '<')\
               .replace('&gt;', '>')\
               .replace('&quot;', '"')\
               .replace('&#39;', "'")\
               .replace('&ndash;', '–')\
               .replace('&mdash;', '—')
    
    # Clean up extra whitespace
    text = ' '.join(text.split())
    
    return text.strip()

@bp.route('/search', methods=['GET', 'POST'])
def search():
    """Search for books using Google Books API"""
    query = request.form.get('query') or request.args.get('query')
    page = request.args.get('page', 1, type=int)
    results_per_page = 40
    
    if not query:
        return render_template('books/search.html', results_per_page=results_per_page)
    
    try:
        if not GOOGLE_BOOKS_API_KEY:
            flash('API key not found', 'error')
            return render_template('books/search.html', results_per_page=results_per_page)
        
        # Get existing books from database for comparison
        db = create_session()
        existing_books = {book.google_books_id: book.status 
                         for book in db.query(Book).all()}
        
        # Clean up the query if it's a subject search
        if query.startswith('subject:'):
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
        
        return render_template('books/search.html', 
                             results=books, 
                             query=query,
                             page=page,
                             total_pages=total_pages,
                             total_items=total_items,
                             results_per_page=results_per_page)
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        flash(f'Error searching books: {str(e)}')
        return render_template('books/search.html', results_per_page=results_per_page)

@bp.route('/add', methods=['POST'])
@login_required
def add():
    db = create_session()
    try:
        # Check if book already exists
        google_books_id = request.form.get('id')
        existing_book = db.query(Book).filter_by(google_books_id=google_books_id, user_id=current_user.id).first()
        
        if existing_book:
            flash('Book already exists in your library', 'warning')
            return redirect(url_for('main.index'))
        
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
            etag=request.form.get('etag'),
            self_link=request.form.get('self_link'),
            print_type=request.form.get('print_type'),
            maturity_rating=request.form.get('maturity_rating'),
            preview_link=request.form.get('preview_link'),
            info_link=request.form.get('info_link'),
            canonical_volume_link=request.form.get('canonical_volume_link'),
            content_version=request.form.get('content_version'),
            is_ebook=request.form.get('is_ebook') == 'true',
            user_id=current_user.id
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
    
    return redirect(url_for('main.index'))

@bp.route('/book/<book_id>')
def detail(book_id):  # renamed from book_detail for blueprint consistency
    """Display details for a specific book from DB or Google Books"""
    db = create_session()
    try:
        # First check if it's in our database
        book = db.query(Book).filter_by(id=book_id).first()
        
        # If not in DB, check if it's a Google Books ID
        if not book:
            try:
                service = build('books', 'v1', developerKey=GOOGLE_BOOKS_API_KEY)
                result = service.volumes().get(volumeId=book_id).execute()
                
                # Create a book-like object from Google Books data
                volume_info = result.get('volumeInfo', {})
                image_links = volume_info.get('imageLinks', {})
                
                book = {
                    'id': result['id'],
                    'title': volume_info.get('title', 'Unknown Title'),
                    'authors': ', '.join(volume_info.get('authors', ['Unknown Author'])),
                    'published_date': volume_info.get('publishedDate', ''),
                    'description': strip_html_tags(volume_info.get('description', '')),
                    'page_count': volume_info.get('pageCount'),
                    'categories': ', '.join(volume_info.get('categories', [])),
                    'language': volume_info.get('language'),
                    'publisher': volume_info.get('publisher'),
                    'thumbnail': image_links.get('thumbnail', ''),
                    'small_thumbnail': image_links.get('smallThumbnail', ''),
                    'isbn': next((i['identifier'] for i in volume_info.get('industryIdentifiers', []) 
                                if i['type'] == 'ISBN_10'), ''),
                    'isbn13': next((i['identifier'] for i in volume_info.get('industryIdentifiers', []) 
                                  if i['type'] == 'ISBN_13'), ''),
                    'preview_link': volume_info.get('previewLink', ''),
                    'info_link': volume_info.get('infoLink', ''),
                    'is_google_books': True  # Flag to indicate this is from Google Books
                }
                
                return render_template('books/detail.html', 
                                    book=book,
                                    is_google_books=True,
                                    back_url=request.referrer or url_for('main.index'))
                                    
            except Exception as e:
                flash('Book not found', 'error')
                return redirect(url_for('main.index'))
        
        # Get the referrer but exclude the edit page
        referrer = request.referrer
        if referrer and '/edit' not in referrer:
            back_url = referrer
        else:
            back_url = url_for('shelf.view', shelf=book.status)
            
        return render_template('books/detail.html', 
                             book=book,
                             is_google_books=False,
                             current_shelf=book.status,
                             back_url=back_url)
    finally:
        db.close()

@bp.route('/update_status/<book_id>', methods=['POST'])
@login_required
def update_status(book_id):
    """Update a book's status"""
    new_status = request.form.get('status')
    db = create_session()
    try:
        book = db.query(Book).filter_by(id=book_id, user_id=current_user.id).first()
        if not book:
            flash('Book not found', 'error')
            return redirect(url_for('main.index'))
            
        if new_status == 'remove':
            db.delete(book)
            flash('Book removed from your library', 'success')
        else:
            book.status = new_status
            if new_status == 'read':
                book.date_read = datetime.now()
            flash(f'Book moved to "{new_status}" shelf', 'success')
            
        db.commit()
        return redirect(request.referrer or url_for('main.index'))
    except Exception as e:
        db.rollback()
        flash(f'Error updating book status: {str(e)}', 'error')
    finally:
        db.close()
    return redirect(request.referrer or url_for('main.index'))

@bp.route('/edit/<book_id>', methods=['GET', 'POST'])
@login_required
def edit(book_id):
    db = create_session()
    try:
        book = db.query(Book).filter_by(id=book_id, user_id=current_user.id).first()
        if not book:
            flash('Book not found', 'error')
            return redirect(url_for('main.index'))

        if request.method == 'POST':
            if 'cancel' in request.form:
                return redirect(url_for('books.detail', book_id=book_id))

            # Handle Google Books refresh
            should_refresh = 'refresh_google' in request.form
            
            if should_refresh:
                google_id = request.form.get('google_books_id') or book.google_books_id
                try:
                    service = build('books', 'v1', developerKey=GOOGLE_BOOKS_API_KEY)
                    result = service.volumes().get(volumeId=google_id).execute()
                    
                    # Extract volume info and create preview data
                    volume_info = result.get('volumeInfo', {})
                    image_links = volume_info.get('imageLinks', {})
                    
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
                    
                    return render_template('books/edit.html', book=book, preview_data=preview_data)
                    
                except Exception as e:
                    flash(f'Error refreshing book data: {str(e)}', 'error')

            # Handle manual field updates
            else:
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
            return redirect(url_for('books.detail', book_id=book_id))

        return render_template('books/edit.html', book=book)
    finally:
        db.close()

@bp.route('/category/<path:category>')
def category(category):  # renamed from category_view for blueprint consistency
    """View books in a specific category. Using path:category to handle slashes"""
    db = create_session()
    try:
        # Normalize the category string for database search
        search_category = category.replace(' / ', '/').strip()
        
        # Get all books in this category, ordered by read date
        books = db.query(Book)\
            .filter(Book.categories.ilike(f'%{search_category}%'))\
            .filter(Book.status == 'read')\
            .order_by(Book.date_read.desc())\
            .all()
            
        return render_template('books/category.html',
                             category=category,
                             books=books)
    finally:
        db.close()
