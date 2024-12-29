import pytest
from utils.email_service import send_email
from unittest.mock import patch, MagicMock

def test_email_development_mode(app):
    """Test email sending in development mode"""
    app.config['MAIL_SUPPRESS_SEND'] = True
    
    with app.app_context():
        result = send_email(
            subject='Test Email',
            recipient='test@example.com',
            template='test',
            name='Test User'
        )
        assert result is True

def test_email_oauth2_mode(app, monkeypatch):
    """Test email sending with OAuth2"""
    app.config.update({
        'MAIL_SUPPRESS_SEND': False,
        'MAIL_USE_OAUTH2': True,
        'MAIL_DEFAULT_SENDER': 'noreply@readkeeper.com',
        'OAUTH_TOKEN_DATA': {
            'token': 'test_token',
            'refresh_token': 'test_refresh',
            'token_uri': 'https://oauth2.googleapis.com/token',
            'client_id': 'test_client_id',
            'client_secret': 'test_secret',
            'scopes': ['https://www.googleapis.com/auth/gmail.send']
        }
    })

    # Mock Gmail API service
    mock_execute = MagicMock(return_value={'id': 'test_message_id'})
    mock_send = MagicMock()
    mock_send.execute = mock_execute
    mock_messages = MagicMock()
    mock_messages.send = MagicMock(return_value=mock_send)
    mock_users = MagicMock()
    mock_users.messages = MagicMock(return_value=mock_messages)
    mock_service = MagicMock()
    mock_service.users = MagicMock(return_value=mock_users)

    with patch('utils.email_service.build', return_value=mock_service):
        with app.app_context():
            result = send_email(
                subject='Test Email',
                recipient='test@example.com',
                template='test',
                name='Test User'
            )
            assert result is True

            # Verify Gmail API was called
            mock_service.users.assert_called_once()
            mock_users.messages.assert_called_once()
            mock_messages.send.assert_called_once()

def test_email_smtp_mode(app):
    """Test email sending with regular SMTP"""
    app.config.update({
        'MAIL_SUPPRESS_SEND': False,
        'MAIL_USE_OAUTH2': False,
        'MAIL_DEFAULT_SENDER': 'noreply@readkeeper.com',
        'MAIL_USERNAME': 'test@example.com',
        'MAIL_PASSWORD': 'test_password',
        'MAIL_SERVER': 'smtp.example.com',
        'MAIL_PORT': 587,
        'MAIL_USE_TLS': True
    })
    
    with patch('flask_mail.Mail.send') as mock_send:
        with app.app_context():
            result = send_email(
                subject='Test Email',
                recipient='test@example.com',
                template='test',
                name='Test User'
            )
            assert result is True
            mock_send.assert_called_once()

def test_email_missing_template(app):
    """Test email sending with missing template"""
    with app.app_context():
        result = send_email(
            subject='Test Email',
            recipient='test@example.com',
            template='nonexistent',
            name='Test User'
        )
        assert result is False

def test_email_oauth2_no_token(app):
    """Test email sending with OAuth2 but no token"""
    app.config.update({
        'MAIL_SUPPRESS_SEND': False,
        'MAIL_USE_OAUTH2': True,
        'OAUTH_TOKEN_DATA': None
    })
    
    # Ensure no token file exists
    with patch('utils.email_service.load_oauth_token', return_value=None):
        with app.app_context():
            result = send_email(
                subject='Test Email',
                recipient='test@example.com',
                template='test',
                name='Test User'
            )
            assert result is False 