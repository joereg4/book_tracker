from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from helper import create_session
from models import User
from sqlalchemy.orm import joinedload
from werkzeug.security import check_password_hash, generate_password_hash

bp = Blueprint('profile', __name__)

@bp.route('/profile')
@login_required
def view():
    db = create_session()
    try:
        # Get fresh user object with books relationship loaded
        user = db.get(User, current_user.id, options=[
            joinedload(User.books)
        ])
        return render_template('profile/view.html', user=user)
    finally:
        db.close()

@bp.route('/profile/update_email', methods=['POST'])
@login_required
def update_email():
    db = create_session()
    try:
        new_email = request.form.get('email')
        if not new_email:
            flash('Email is required.', 'error')
            return redirect(url_for('profile.view'))
            
        user = db.get(User, current_user.id)
        user.email = new_email
        db.commit()
        flash('Email updated successfully.', 'success')
        return redirect(url_for('profile.view'))
    finally:
        db.close() 

@bp.route('/profile/update_password', methods=['POST'])
@login_required
def update_password():
    db = create_session()
    try:
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        if not all([current_password, new_password, confirm_password]):
            flash('All password fields are required.', 'error')
            return redirect(url_for('profile.view'))

        user = db.get(User, current_user.id)
        
        if not check_password_hash(user.password, current_password):
            flash('Current password is incorrect.', 'error')
            return redirect(url_for('profile.view'))
            
        if new_password != confirm_password:
            flash('New passwords do not match.', 'error')
            return redirect(url_for('profile.view'))
            
        user.password = generate_password_hash(new_password)
        db.commit()
        flash('Password updated successfully.', 'success')
        return redirect(url_for('profile.view'))
    finally:
        db.close() 

@bp.route('/profile/delete', methods=['GET', 'POST'])
@login_required
def delete_account():
    if request.method == 'GET':
        return render_template('profile/delete.html')
        
    db = create_session()
    try:
        confirmation = request.form.get('confirmation')
        if confirmation != 'DELETE':
            flash('Please type DELETE to confirm account deletion.', 'error')
            return redirect(url_for('profile.delete_account'))

        user = db.get(User, current_user.id)
        if user:
            # Delete all user's books first
            for book in user.books:
                db.delete(book)
            # Then delete the user
            db.delete(user)
            db.commit()
            
            # Log the user out
            from flask_login import logout_user
            logout_user()
            
            flash('Your account has been permanently deleted.', 'success')
            return redirect(url_for('main.index'))
        
        flash('User not found.', 'error')
        return redirect(url_for('profile.view'))
    finally:
        db.close() 