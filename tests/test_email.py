import pytest
from utils.email_service import send_email
from unittest.mock import patch, MagicMock

def test_email_development_mode(app, mail):
    """Test email sending in development mode with MailHog"""
    with app.app_context():
        result = send_email(
            subject='Test Email',
            recipient='test@example.com',
            template='test',
            name='Test User'
        )
        assert result is True

def test_email_smtp_mode(app, mail):
    """Test email sending with SMTP"""
    app.config.update({
        'MAIL_SUPPRESS_SEND': False,
        'MAIL_SERVER': 'localhost',
        'MAIL_PORT': 1026,
        'MAIL_USE_TLS': False,
        'MAIL_DEFAULT_SENDER': 'noreply@dev-mail.readkeeper.com'
    })

    with app.app_context():
        result = send_email(
            subject='Test Email',
            recipient='test@example.com',
            template='test',
            name='Test User'
        )
        assert result is True

def test_email_missing_template(app, mail):
    """Test email sending with missing template"""
    with app.app_context():
        result = send_email(
            subject='Test Email',
            recipient='test@example.com',
            template='nonexistent',
            name='Test User'
        )
        assert result is False

def test_welcome_email(app, mail, test_user):
    """Test sending welcome email"""
    with app.app_context():
        result = send_email(
            subject='Welcome to ReadKeeper',
            recipient=test_user.email,
            template='welcome',
            name=test_user.username
        )
        assert result is True

def test_password_reset_email(app, mail, test_user):
    """Test sending password reset email"""
    with app.app_context():
        result = send_email(
            subject='Reset Your ReadKeeper Password',
            recipient=test_user.email,
            template='password_reset',
            name=test_user.username,
            reset_url='http://localhost:5000/reset-password?token=test-token'
        )
        assert result is True 