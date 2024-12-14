from flask import Blueprint, render_template, request
from models import Book, db
from flask_login import current_user
from sqlalchemy import text

bp = Blueprint('shelf', __name__)

@bp.route('/shelf/<shelf>')
def view(shelf):
    """Display books on a specific shelf"""
    titles = {
        'to_read': 'To Read',
        'reading': 'Currently Reading',
        'read': 'Read'
    }
    
    try:
        # Get search query
        search_query = request.args.get('search', '').strip()
        
        # Base query
        query = Book.query.filter(
            Book.status == shelf,
            Book.user_id == current_user.id
        )
        
        # Apply search if provided
        if search_query:
            # Create a search pattern that handles variations
            search_terms = []
            for term in search_query.lower().split():
                # Add exact match
                search_terms.append(f'{term}*')
                
                # Add common spelling variations
                if 'o' in term:
                    search_terms.append(term.replace('o', 'u') + '*')
                if 'u' in term:
                    search_terms.append(term.replace('u', 'o') + '*')
            
            # Join all search patterns with OR
            search_pattern = ' OR '.join(search_terms)
            
            # Get matching IDs from FTS table
            sql = text('SELECT rowid FROM books_fts WHERE books_fts MATCH :pattern')
            matching_ids = [r[0] for r in db.session.execute(sql, {'pattern': search_pattern})]
            
            # Filter books by matching IDs
            query = query.filter(Book.id.in_(matching_ids))

        # Apply ordering
        if shelf == 'read':
            query = query.order_by(
                Book.date_read.desc().nulls_last(),
                Book.created_at.desc()
            )
        else:
            query = query.order_by(Book.created_at.desc())
        
        books = query.all()
        return render_template('shelf/view.html',
                             books=books,
                             title=titles.get(shelf, 'Books'),
                             current_shelf=shelf)
                             
    except Exception as e:
        print(f"Search error: {str(e)}")
        books = []
        return render_template('shelf/view.html',
                             books=books,
                             title=titles.get(shelf, 'Books'),
                             current_shelf=shelf,
                             error="An error occurred while searching")