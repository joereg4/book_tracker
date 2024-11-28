from flask import Blueprint, render_template, request, redirect, url_for, flash
from sqlalchemy import create_engine
from datetime import datetime
import re
from googleapiclient.discovery import build
import os
from helper import SessionLocal
from models import Book

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
        db = SessionLocal()
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
def add():
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
