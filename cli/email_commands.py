import click
from flask.cli import with_appcontext
from utils.email_service import send_email
from flask import current_app
from utils.oauth2 import get_oauth2_credentials
from routes.monitoring import redis_client
import webbrowser
import os
import json
import logging

logger = logging.getLogger(__name__)
REDIS_TOKEN_KEY = 'oauth2_token'

@click.group(name='email-cli')
def email_cli():
    """Email management commands"""
    pass

def load_oauth_token():
    """Load OAuth token from Redis"""
    try:
        token_data = redis_client.get(REDIS_TOKEN_KEY)
        if token_data:
            return json.loads(token_data)
        return None
    except Exception as e:
        logger.error(f"Error loading token from Redis: {str(e)}")
        return None

def save_oauth_token(token_data):
    """Save OAuth token to Redis"""
    try:
        redis_client.set(REDIS_TOKEN_KEY, json.dumps(token_data))
        logger.debug("Token saved to Redis successfully")
    except Exception as e:
        logger.error(f"Error saving token to Redis: {str(e)}")
        raise click.ClickException("Failed to save OAuth token")

@email_cli.command()
@click.argument('recipient')
@with_appcontext
def test(recipient):
    """Send a test email to verify configuration"""
    if current_app.config.get('MAIL_USE_OAUTH2'):
        token_data = load_oauth_token()
        if not token_data or not token_data.get('refresh_token'):
            flow = get_oauth2_credentials()
            authorization_url, _ = flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true',
                prompt='consent'  # Force consent screen to get refresh token
            )
            click.echo(f"\nPlease authorize email access by visiting:\n{authorization_url}\n")
            click.echo("After authorization, copy the 'code' parameter from the redirect URL and run:")
            click.echo(f"flask email-cli authorize <code>")
            webbrowser.open(authorization_url)
            return
        
        # Set the token in app config
        current_app.config['OAUTH_TOKEN_DATA'] = token_data
    
    success = send_email(
        'Test Email from ReadKeeper',
        recipient,
        'test_email',
        name=recipient.split('@')[0]
    )
    
    if success:
        click.echo(f"Test email sent to {recipient}")
    else:
        click.echo("Failed to send test email", err=True)
        raise click.ClickException("Email sending failed")

@email_cli.command()
@click.argument('code')
@with_appcontext
def authorize(code):
    """Complete OAuth authorization with the provided code"""
    try:
        flow = get_oauth2_credentials()
        flow.fetch_token(code=code)
        
        credentials = flow.credentials
        if not credentials.refresh_token:
            raise click.ClickException("No refresh token received. Please try again.")
            
        token_data = {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes
        }
        
        save_oauth_token(token_data)
        click.echo("Authorization successful! You can now send emails.")
        
    except Exception as e:
        click.echo(f"Authorization failed: {str(e)}", err=True)
        raise click.ClickException("OAuth authorization failed")

def init_app(app):
    """Register CLI commands"""
    app.cli.add_command(email_cli) 