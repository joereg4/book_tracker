from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import User
from helper import create_session

bp = Blueprint('auth', __name__)

@bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        db = create_session()
        try:
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')

            user = db.query(User).filter_by(username=username).first()
            if user:
                flash('Username already exists')
                return redirect(url_for('auth.signup'))

            user = db.query(User).filter_by(email=email).first()
            if user:
                flash('Email already registered')
                return redirect(url_for('auth.signup'))

            new_user = User(
                username=username,
                email=email,
                password=generate_password_hash(password)
            )

            db.add(new_user)
            db.commit()

            flash('Registration successful! Please log in.')
            return redirect(url_for('auth.login'))
        finally:
            db.close()

    return render_template('auth/signup.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        db = create_session()
        try:
            username = request.form.get('username')
            password = request.form.get('password')

            user = db.query(User).filter_by(username=username).first()
            if user and check_password_hash(user.password, password):
                login_user(user)
                return redirect(url_for('main.index'))

            flash('Invalid username or password')
        finally:
            db.close()
    return render_template('auth/login.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))
