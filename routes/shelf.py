from flask import Blueprint, render_template, request
from models import Book, db
from flask_login import current_user
from sqlalchemy import text
import re

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
            # Clean and prepare search terms
            search_terms = []
            for term in search_query.lower().split():
                # Escape special characters
                term = re.sub(r'[^\w\s]', ' ', term)
                term = term.strip()
                if term:
                    # Add exact match with prefix
                    search_terms.append(f'"{term}"*')
                    
                    # Add common spelling variations
                    if 'o' in term:
                        search_terms.append(f'"{term.replace("o", "u")}"*')
                    if 'u' in term:
                        search_terms.append(f'"{term.replace("u", "o")}"*')
            
            # Join all search patterns with OR
            search_pattern = ' OR '.join(search_terms)
            
            if search_pattern:
                # Get matching IDs from FTS table
                sql = text("""
                    SELECT rowid FROM books_fts 
                    WHERE books_fts MATCH :pattern 
                    ORDER BY rank
                """)
                matching_ids = [r[0] for r in db.session.execute(sql, {'pattern': search_pattern})]
                
                # Filter books by matching IDs
                if matching_ids:
                    query = query.filter(Book.id.in_(matching_ids))
                else:
                    # If no FTS matches, return empty result
                    query = query.filter(Book.id == None)

        # Apply ordering
        if shelf == 'read':
            query = query.order_by(
                Book.date_read.desc().nulls_last(),
                Book.created_at.desc()
            )
        else:
            query = query.order_by(Book.created_at.desc())
        
        books = query.all()
        
        # Get the count for the search results message
        count = len(books)
        search_message = f'Found {count} books matching "{search_query}"' if search_query else None
        
        return render_template('shelf/view.html',
                             books=books,
                             title=titles.get(shelf, 'Books'),
                             current_shelf=shelf,
                             search_query=search_query,
                             search_message=search_message)
                             
    except Exception as e:
        print(f"Search error: {str(e)}")
        books = []
        return render_template('shelf/view.html',
                             books=books,
                             title=titles.get(shelf, 'Books'),
                             current_shelf=shelf,
                             error="An error occurred while searching")