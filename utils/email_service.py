from flask import current_app, render_template
from flask_mail import Message
from extensions import mail
import logging

logger = logging.getLogger(__name__)

def send_email(subject, recipient, template, **kwargs):
    """
    Send an email using either SendGrid or development mode
    
    Args:
        subject (str): Email subject
        recipient (str): Recipient email address
        template (str): Name of the template (without extension)
        **kwargs: Variables to pass to the template
    """
    msg = Message(
        subject,
        recipients=[recipient],
        sender=current_app.config['MAIL_DEFAULT_SENDER']
    )
    
    # Render template with kwargs
    msg.body = render_template(f'email/{template}.txt', **kwargs)
    msg.html = render_template(f'email/{template}.html', **kwargs)
    
    if current_app.config['MAIL_SUPPRESS_SEND']:
        # Development mode: Log email instead of sending
        logger.info(f"""
        ----------------------
        Email Details:
        ----------------------
        To: {recipient}
        Subject: {subject}
        Body:
        {msg.body}
        ----------------------
        """)
        return True
    
    try:
        mail.send(msg)
        return True
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        return False 