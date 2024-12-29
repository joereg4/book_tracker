from flask import Blueprint, render_template
from models import Book
from flask_login import current_user

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    if not current_user.is_authenticated:
        return render_template('landing.html')
        
    # Get user's books for different shelves
    to_read = Book.query.filter_by(user_id=current_user.id, status='to_read').all()
    reading = Book.query.filter_by(user_id=current_user.id, status='reading').all()
    read = Book.query.filter_by(user_id=current_user.id, status='read').all()
    
    return render_template('main/home.html',
                         to_read=to_read,
                         reading=reading,
                         read=read)