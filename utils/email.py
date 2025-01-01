from flask import current_app
from flask_mail import Message, Mail
import logging
from utils.email_service import send_email

mail = Mail()

def send_password_reset_email(user, reset_url):
    """Send a password reset email to the user."""
    return send_email(
        subject='Reset Your ReadKeeper Password',
        recipient=user.email,
        template='password_reset',
        name=user.username,
        reset_url=reset_url
    )

def send_welcome_email(user):
    """Send a welcome email to a new user."""
    return send_email(
        subject='Welcome to ReadKeeper',
        recipient=user.email,
        template='welcome',
        name=user.username
    ) 