from flask import Blueprint, render_template
from flask_login import login_required, current_user
from helper import create_session
from models import User
from sqlalchemy.orm import joinedload

bp = Blueprint('profile', __name__)

@bp.route('/profile')
@login_required
def view():
    db = create_session()
    try:
        # Get fresh user object with books relationship loaded
        user = db.query(User).options(
            joinedload(User.books)
        ).get(current_user.id)
        return render_template('profile/view.html', user=user)
    finally:
        db.close() 