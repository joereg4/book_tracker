from flask import Blueprint, render_template, request, current_app
from models import Book, db
from flask_login import current_user
from sqlalchemy import text, or_, desc

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
            # Check if we're using PostgreSQL or SQLite
            is_postgres = 'postgresql' in current_app.config['SQLALCHEMY_DATABASE_URI']
            
            if is_postgres:
                # Use PostgreSQL's full-text search with existing search_vector
                search_query_sql = text("plainto_tsquery('books_fts_config', :search_terms)")
                
                # Add the rank as a column to the query
                rank_sql = text("ts_rank(search_vector, plainto_tsquery('books_fts_config', :search_terms)) as search_rank")
                query = query.add_columns(rank_sql)
                
                # Add the search filter
                query = query.filter(
                    text("search_vector @@ plainto_tsquery('books_fts_config', :search_terms)")
                ).params(search_terms=search_query)
                
                # Order by the rank column
                query = query.order_by(text("search_rank DESC"))
                
                # Execute query and extract just the Book objects
                results = query.all()
                books = [r[0] for r in results]
            else:
                # SQLite fallback for tests
                query = query.filter(or_(
                    Book.title.ilike(f'%{search_query}%'),
                    Book.authors.ilike(f'%{search_query}%'),
                    Book.description.ilike(f'%{search_query}%'),
                    Book.categories.ilike(f'%{search_query}%')
                ))
                
                # Execute query
                books = query.all()
        else:
            # If no search, just get all books
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