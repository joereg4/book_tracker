from flask import current_app, render_template
from flask_mail import Message
from extensions import mail
import logging
import sys

# Configure logging to show in console
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

def send_email(subject, recipient, template, **kwargs):
    """Send an email using SMTP (MailHog in development, Postfix in production)."""
    try:
        # Render both text and HTML versions of the email
        text = render_template(f'email/{template}.txt', **kwargs)
        html = render_template(f'email/{template}.html', **kwargs)

        msg = Message(
            subject=subject,
            recipients=[recipient],
            body=text,
            html=html,
            sender=current_app.config['MAIL_DEFAULT_SENDER']
        )
        mail.send(msg)
        
        env = 'development' if current_app.config.get('FLASK_ENV') == 'development' else 'production'
        logger.info(f"{env.capitalize()} email sent to {recipient}")
        return True
        
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")
        return False 