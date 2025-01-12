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
        # Log full mail configuration
        mail_config = {k: v for k, v in current_app.config.items() if k.startswith('MAIL_')}
        logger.debug(f"Full mail configuration: {mail_config}")
        
        # Render both text and HTML versions of the email
        text = render_template(f'email/{template}.txt', **kwargs)
        html = render_template(f'email/{template}.html', **kwargs)
        
        logger.debug(f"Rendered templates: {template}.txt and {template}.html")
        logger.debug(f"Text content: {text[:100]}...")
        logger.debug(f"HTML content: {html[:100]}...")

        msg = Message(
            subject=subject,
            recipients=[recipient],
            body=text,
            html=html,
            sender=current_app.config['MAIL_DEFAULT_SENDER']
        )
        logger.debug(f"Created message object: subject={subject}, recipient={recipient}, sender={current_app.config['MAIL_DEFAULT_SENDER']}")
        
        # Log Flask-Mail object configuration
        logger.debug(f"Flask-Mail configuration: {vars(mail)}")
        
        mail.send(msg)
        logger.debug("Message sent successfully through Flask-Mail")
        
        env = 'development' if current_app.config.get('FLASK_ENV') == 'development' else 'production'
        logger.info(f"{env.capitalize()} email sent to {recipient}")
        return True
        
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")
        logger.exception("Full traceback:")
        return False 