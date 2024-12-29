from flask import Blueprint, current_app, redirect, request, session, url_for, flash, render_template_string
from utils.oauth2 import get_oauth2_credentials
import json
import logging

logger = logging.getLogger(__name__)
bp = Blueprint('oauth', __name__)

@bp.route('/oauth2callback')
def oauth2callback():
    """Handle OAuth2 callback from Google"""
    try:
        # Get authorization code from request
        code = request.args.get('code')
        if not code:
            flash('No authorization code received', 'error')
            return redirect(url_for('main.index'))
        
        # Display the code to the user
        template = """
        <h1>Authorization Code</h1>
        <p>Please copy this code and run the following command in your terminal:</p>
        <pre>flask email-cli authorize {{ code }}</pre>
        <p>Code: <strong>{{ code }}</strong></p>
        <hr>
        <a href="{{ url_for('main.index') }}">Return to Home</a>
        """
        return render_template_string(template, code=code)
        
    except Exception as e:
        logger.error(f"OAuth2 callback error: {str(e)}")
        flash('Failed to authorize email access', 'error')
        return redirect(url_for('main.index')) 