from flask import Blueprint, render_template, request
from sqlalchemy import func, extract
from datetime import datetime
from collections import Counter
from models import Book, db
from flask_login import current_user, login_required

bp = Blueprint('stats', __name__, url_prefix='/stats')

@bp.route('/')
@login_required
def dashboard():
    try:
        # Get selected year from query params
        selected_year = request.args.get('year', type=int)
        selected_author = request.args.get('author')
        
        # Calculate overall stats
        total_books = db.session.query(Book).filter_by(user_id=current_user.id).count()
        current_year = datetime.now().year
        books_this_year = db.session.query(Book)\
            .filter_by(user_id=current_user.id)\
            .filter(Book.date_read.isnot(None))\
            .filter(extract('year', Book.date_read) == current_year)\
            .count()
        
        # Calculate total pages
        total_pages = db.session.query(func.sum(Book.page_count))\
            .filter_by(user_id=current_user.id)\
            .filter(Book.status == 'read')\
            .scalar() or 0
            
        # Get books by year read (instead of publication year)
        year_column = extract('year', Book.date_read).label('year')
        years = db.session.query(
            year_column,
            func.count().label('count')
        ).filter_by(user_id=current_user.id)\
         .filter(Book.status == 'read')\
         .filter(Book.date_read.isnot(None))\
         .group_by('year')\
         .order_by(year_column.desc())\
         .all()
        
        # Get most read author with count
        most_read_author = db.session.query(
            Book.authors,
            func.count().label('count')
        ).filter_by(user_id=current_user.id)\
         .filter(Book.authors.isnot(None))\
         .group_by(Book.authors)\
         .order_by(-func.count())\
         .first()
        
        # Get books for selected year or author
        books = None
        if selected_year:
            books = db.session.query(Book)\
                .filter(Book.status == 'read')\
                .filter(extract('year', Book.date_read) == selected_year)\
                .order_by(Book.date_read.desc())\
                .all()
        elif selected_author:
            books = db.session.query(Book)\
                .filter(Book.authors == selected_author)\
                .order_by(Book.date_read.desc())\
                .all()

        # Get categories and their counts
        categories = []
        for book in db.session.query(Book).filter_by(user_id=current_user.id).all():
            if book.categories:
                cats = [c.strip() for c in book.categories.split(',')]
                categories.extend(cats)
        
        category_counts = Counter(categories)
        top_categories = category_counts.most_common(15)  # Get top 15 categories
        max_category_count = max(count for _, count in top_categories) if top_categories else 1
        
        # Get most read publisher
        most_read_publisher = db.session.query(
            Book.publisher,
            func.count().label('count')
        ).filter_by(user_id=current_user.id)\
         .filter(Book.publisher.isnot(None))\
         .group_by(Book.publisher)\
         .order_by(-func.count())\
         .first()
        
        # Calculate average pages per book
        avg_pages = db.session.query(func.avg(Book.page_count))\
            .filter_by(user_id=current_user.id)\
            .filter(Book.page_count.isnot(None))\
            .scalar() or 0

        # Get longest and shortest books
        longest_book = db.session.query(Book)\
            .filter_by(user_id=current_user.id)\
            .filter(Book.page_count.isnot(None))\
            .filter(Book.page_count > 0)\
            .filter(Book.status == 'read')\
            .order_by(Book.page_count.desc())\
            .first()
            
        shortest_book = db.session.query(Book)\
            .filter_by(user_id=current_user.id)\
            .filter(Book.page_count.isnot(None))\
            .filter(Book.page_count > 0)\
            .filter(Book.status == 'read')\
            .order_by(Book.page_count.asc())\
            .first()

        return render_template('stats/dashboard.html',
                            selected_author=selected_author,
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
                            most_read_author_count=most_read_author[1] if most_read_author else 0,
                            avg_pages=avg_pages,
                            longest_book=longest_book,
                            shortest_book=shortest_book,)
    finally:
        pass