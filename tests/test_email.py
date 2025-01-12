import pytest
from flask import Flask
from flask_mail import Mail, Message
from utils.email_service import send_email
from dotenv import load_dotenv

def test_mailhog_development(app):
    """Test email sending in development mode using MailHog"""
    app.config.update(
        MAIL_SERVER='localhost',
        MAIL_PORT=1026,  # MailHog SMTP port
        MAIL_USE_TLS=False,
        MAIL_USERNAME=None,
        MAIL_PASSWORD=None,
        MAIL_DEFAULT_SENDER='noreply@dev-mail.readkeeper.com'
    )
    
    mail = Mail(app)
    
    with app.app_context():
        msg = Message(
            subject="Test Email from ReadKeeper",
            recipients=["test@example.com"],
            body="This is a test email from the ReadKeeper development environment."
        )
        mail.send(msg)
        assert True  # If we get here without exception, the email was sent

def test_postfix_smtp(app):
    """Test email sending using Postfix SMTP with TLS"""
    app.config.update(
        MAIL_SERVER='localhost',
        MAIL_PORT=587,  # Postfix SMTP port with STARTTLS
        MAIL_USE_TLS=True,
        MAIL_USERNAME='noreply',
        MAIL_PASSWORD='your_secure_password',
        MAIL_DEFAULT_SENDER='noreply@dev-mail.readkeeper.com'
    )
    
    mail = Mail(app)
    mail.init_app(app)
    
    with app.app_context():
        success = send_email(
            subject="Test SMTP Email",
            recipient="test@example.com",
            template="test",
            name="Test User"
        )
        assert success is True 