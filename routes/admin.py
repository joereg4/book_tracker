from flask import Blueprint, render_template
from flask_login import login_required
from utils.decorators import admin_required
from models import User, db
from datetime import datetime, UTC, timedelta

bp = Blueprint('admin', __name__, url_prefix='/admin')

@bp.route('/')
@login_required
@admin_required
def dashboard():
    """Admin dashboard showing system metrics"""
    # Get user statistics
    total_users = User.query.count()
    active_users = User.query.filter(
        User.last_seen >= datetime.now(UTC) - timedelta(days=30)
    ).count()
    admin_users = User.query.filter_by(is_admin=True).count()
    
    # Get recent users
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html',
                         total_users=total_users,
                         active_users=active_users,
                         admin_users=admin_users,
                         recent_users=recent_users) 