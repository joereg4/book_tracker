from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta, UTC
import secrets
from models import User
from extensions import db, limiter
from utils.email import send_password_reset_email
from routes.monitoring import record_rate_limit_hit, redis_client, DummyRedis

bp = Blueprint('auth', __name__)

def check_login_rate_limit(ip_address):
    """Check if IP has exceeded login rate limit"""
    try:
        if isinstance(redis_client, DummyRedis):
            return False
        
        now = datetime.now(UTC)
        minute_key = f"login_attempts:{ip_address}:{now.strftime('%Y-%m-%d:%H:%M')}"
        
        attempts = int(redis_client.get(minute_key) or 0)
        return attempts >= 5  # Return True if limit exceeded
    except:
        return False  # Don't block on Redis errors

@bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Validate required fields
        if not all([username, email, password, confirm_password]):
            flash('All fields are required.', 'error')
            return redirect(url_for('auth.signup'))
        
        # Check if passwords match
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return redirect(url_for('auth.signup'))

        # Check if username exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'error')
            return redirect(url_for('auth.signup'))

        # Check if email exists
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'error')
            return redirect(url_for('auth.signup'))

        new_user = User(
            username=username,
            email=email,
            password=generate_password_hash(password)
        )

        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/signup.html')

@bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute", methods=['POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            flash('Username and password are required.', 'error')
            return render_template('auth/login.html'), 400

        user = User.query.filter_by(username=username).first()
        if not user or not check_password_hash(user.password, password):
            try:
                record_rate_limit_hit('login', request.remote_addr)
            except:
                pass  # Don't fail the request if Redis is unavailable
            
            flash('Invalid username or password', 'error')
            # Return 400 for invalid credentials and ensure user is logged out
            if current_user.is_authenticated:
                logout_user()
            return render_template('auth/login.html'), 400

        # Log out any existing user first
        if current_user.is_authenticated:
            logout_user()
        # Then log in the new user
        login_user(user, remember=True)
        flash('Welcome back!', 'success')
        next_page = request.args.get('next')
        if next_page:
            return redirect(next_page)
        return redirect(url_for('main.index'))
        
    return render_template('auth/login.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        
        if user:
            # Generate reset token
            token = secrets.token_urlsafe(32)
            user.reset_token = token
            user.reset_token_expiry = datetime.now() + timedelta(hours=1)
            db.session.commit()
            
            # Send reset email
            reset_url = url_for('auth.reset_password', token=token, _external=True)
            send_password_reset_email(user, reset_url)
        
        # Always show success message for security
        flash('Reset instructions sent to your email', 'info')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/forgot_password.html')

@bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    user = User.query.filter_by(reset_token=token).first()
    
    if not user or not user.reset_token_expiry or user.reset_token_expiry < datetime.now():
        flash('Invalid or expired reset link', 'error')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash('Password mismatch', 'error')
            return render_template('auth/reset_password.html')
        
        # Update password and clear reset token
        user.password = generate_password_hash(password)
        user.reset_token = None
        user.reset_token_expiry = None
        db.session.commit()
        
        flash('Password updated successfully', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password.html')
