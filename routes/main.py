from flask import Blueprint, render_template
from models import Book
from helper import SessionLocal

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    """Show dashboard view"""
    db = SessionLocal()
    try:
        to_read = db.query(Book).filter_by(status='to_read')\
                   .order_by(Book.created_at.desc()).all()
        reading = db.query(Book).filter_by(status='reading')\
                   .order_by(Book.created_at.desc()).all()
        read = db.query(Book).filter_by(status='read')\
                .order_by(Book.date_read.desc().nulls_last()).all()
        
        return render_template('main/home.html', 
                             to_read=to_read,
                             reading=reading,
                             read=read)
    finally:
        db.close() 