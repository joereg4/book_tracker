from flask import Blueprint, render_template
from datetime import datetime

bp = Blueprint('legal', __name__)

@bp.route('/privacy')
def privacy():
    return render_template('legal/privacy.html', 
                         current_date=datetime.now().strftime('%B %d, %Y'))

@bp.route('/terms')
def terms():
    return render_template('legal/terms.html', 
                         current_date=datetime.now().strftime('%B %d, %Y')) 