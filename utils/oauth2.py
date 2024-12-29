from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from flask import current_app, url_for
import os

def get_oauth2_credentials():
    """Get OAuth2 credentials for Gmail"""
    if not current_app.config.get('MAIL_USE_OAUTH2'):
        return None
        
    client_id = current_app.config.get('MAIL_OAUTH_CLIENT_ID')
    client_secret = current_app.config.get('MAIL_OAUTH_CLIENT_SECRET')
    
    if not (client_id and client_secret):
        raise ValueError("OAuth2 client ID and secret must be configured")
    
    # Use the redirect URI from environment or default to localhost
    redirect_uri = current_app.config.get('MAIL_OAUTH_REDIRECT_URI')
    if not redirect_uri:
        # Default to localhost for development
        redirect_uri = 'http://localhost:5000/oauth2callback'
    
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": client_id,
                "client_secret": client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [redirect_uri]
            }
        },
        scopes=["https://www.googleapis.com/auth/gmail.send"]
    )
    
    flow.redirect_uri = redirect_uri
    return flow 