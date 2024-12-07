from flask import Blueprint, render_template

bp = Blueprint('profile', __name__)

@bp.route('/profile')
def view():
    return render_template('profile/view.html') 