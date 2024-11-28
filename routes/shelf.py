from flask import Blueprint, render_template, request
from models import Book
from helper import SessionLocal

bp = Blueprint('shelf', __name__)

@bp.route('/shelf/<shelf>')
def view(shelf):
    """Display books on a specific shelf"""
    titles = {
        'to_read': 'To Read',
        'reading': 'Currently Reading',
        'read': 'Read'
    }
    
    db = SessionLocal()
    try:
        # Get search query
        search_query = request.args.get('search', '').strip()
        
        # Base query
        query = db.query(Book).filter_by(status=shelf)
        
        # Apply search if provided
        if search_query:
            search_filter = (
                (Book.title.ilike(f'%{search_query}%')) |
                (Book.authors.ilike(f'%{search_query}%')) |
                (Book.description.ilike(f'%{search_query}%')) |
                (Book.publisher.ilike(f'%{search_query}%')) |
                (Book.categories.ilike(f'%{search_query}%'))
            )
            query = query.filter(search_filter)
        
        # Apply ordering
        if shelf == 'read':
            query = query.order_by(Book.date_read.desc().nulls_last(),
                                 Book.created_at.desc())
        else:
            query = query.order_by(Book.created_at.desc())
            
        books = query.all()
            
        return render_template('shelf/view.html',
                             books=books,
                             title=titles.get(shelf, 'Books'),
                             current_shelf=shelf)
    finally:
        db.close()
