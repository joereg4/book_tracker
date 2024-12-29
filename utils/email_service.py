from flask import current_app, render_template
from flask_mail import Message
from extensions import mail
from .oauth2 import get_oauth2_credentials
import logging
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import base64
import os
import json
import sys

# Configure logging to show in console
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

TOKEN_FILE = 'instance/oauth2_token.json'

def load_oauth_token():
    """Load OAuth token from file"""
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'r') as f:
            logger.debug(f"Loading OAuth token from {TOKEN_FILE}")
            data = json.load(f)
            logger.debug(f"Token loaded successfully: {data.keys()}")
            return data
    logger.warning(f"No token file found at {TOKEN_FILE}")
    return None

def create_message(sender, to, subject, text, html):
    """Create a message for an email."""
    message = MIMEMultipart('alternative')
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject

    # Add text and HTML parts
    message.attach(MIMEText(text, 'plain'))
    message.attach(MIMEText(html, 'html'))

    # Encode the message
    raw = base64.urlsafe_b64encode(message.as_bytes())
    raw = raw.decode()
    return {'raw': raw}

def send_email(subject, recipient, template, **kwargs):
    """
    Send an email using Gmail API with OAuth2
    """
    logger.debug("Starting email send process")
    logger.debug(f"Current config: {current_app.config}")
    
    # Render template with kwargs
    try:
        text_body = render_template(f'email/{template}.txt', **kwargs)
        html_body = render_template(f'email/{template}.html', **kwargs)
        logger.debug("Email templates rendered successfully")
    except Exception as e:
        logger.error(f"Failed to render email templates: {str(e)}", exc_info=True)
        return False
    
    if current_app.config.get('MAIL_SUPPRESS_SEND'):
        logger.debug("Email suppressed in development mode")
        logger.info(f"Would have sent email to {recipient}: {subject}")
        return True
    
    try:
        # Get OAuth2 credentials
        if current_app.config.get('MAIL_USE_OAUTH2'):
            logger.debug("Using OAuth2 for authentication")
            token_data = current_app.config.get('OAUTH_TOKEN_DATA') or load_oauth_token()
            if not token_data:
                logger.error("OAuth2 token not found")
                return False
            
            logger.debug("Creating credentials from token data")
            credentials = Credentials(
                token=token_data['token'],
                refresh_token=token_data['refresh_token'],
                token_uri=token_data['token_uri'],
                client_id=token_data['client_id'],
                client_secret=token_data['client_secret'],
                scopes=token_data['scopes']
            )
            
            # Create Gmail API service
            logger.debug("Creating Gmail API service")
            service = build('gmail', 'v1', credentials=credentials)
            
            # Create and send the message
            sender = current_app.config['MAIL_DEFAULT_SENDER']
            message = create_message(sender, recipient, subject, text_body, html_body)
            
            logger.debug("Attempting to send email via Gmail API")
            service.users().messages().send(userId='me', body=message).execute()
            logger.info(f"Email sent successfully to {recipient}")
            return True
        else:
            # Fallback to regular Flask-Mail for non-OAuth2 sending
            msg = Message(
                subject,
                recipients=[recipient],
                sender=current_app.config['MAIL_DEFAULT_SENDER'],
                body=text_body,
                html=html_body
            )
            mail.send(msg)
            logger.info(f"Email sent successfully to {recipient} using Flask-Mail")
            return True
        
    except Exception as e:
        logger.error("Failed to send email")
        logger.error(f"Error type: {type(e).__name__}")
        logger.error(f"Error message: {str(e)}")
        logger.error("Full traceback:", exc_info=True)
        return False 