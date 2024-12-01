from flask import Blueprint, render_template, request
from models import Book
from helper import create_session
from sqlalchemy import text
from sqlalchemy.orm import aliased

bp = Blueprint('shelf', __name__)

@bp.route('/shelf/<shelf>')
def view(shelf):
    """Display books on a specific shelf"""
    titles = {
        'to_read': 'To Read',
        'reading': 'Currently Reading',
        'read': 'Read'
    }
    
    db = create_session()
    try:
        # Get search query
        search_query = request.args.get('search', '').strip()
        
        # Base query
        query = db.query(Book).filter_by(status=shelf)
        
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
            
            # Debug: Print the search terms
            print(f"Search terms: {search_pattern}")
            
            # Create FTS subquery with MATCH operator
            fts_subquery = text("""
                SELECT rowid as id 
                FROM books_fts 
                WHERE books_fts MATCH :search 
                ORDER BY rank
            """).params(search=search_pattern).columns(Book.id).subquery()

            query = db.query(Book).filter(
                Book.status == shelf,
                Book.id.in_(
                    db.query(fts_subquery.c.id)
                )
            ).order_by(Book.created_at.desc())
        else:
            # Default ordering without search
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
