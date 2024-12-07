from flask import Blueprint, render_template
from models import Book
from helper import create_session
from flask_login import current_user

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    """Show dashboard view"""
    if not current_user.is_authenticated:
        # Show empty dashboard for non-authenticated users
        return render_template('main/home.html', 
                             to_read=[],
                             reading=[],
                             read=[])
    
    db = create_session()
    try:
        to_read = db.query(Book).filter_by(
            status='to_read',
            user_id=current_user.id
        ).order_by(Book.created_at.desc()).all()
        
        reading = db.query(Book).filter_by(
            status='reading',
            user_id=current_user.id
        ).order_by(Book.created_at.desc()).all()
        
        read = db.query(Book).filter_by(
            status='read',
            user_id=current_user.id
        ).order_by(Book.date_read.desc().nulls_last()).all()
        
        return render_template('main/home.html', 
                             to_read=to_read,
                             reading=reading,
                             read=read)
    finally:
        db.close() 