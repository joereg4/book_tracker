from flask import current_app
from flask_mail import Message, Mail
import logging

mail = Mail()

def send_password_reset_email(user, reset_url):
    msg = Message('Password Reset Request',
                  sender=current_app.config['MAIL_DEFAULT_SENDER'],
                  recipients=[user.email])
    
    msg.body = f'''To reset your password, visit the following link:
{reset_url}

If you did not make this request, please ignore this email.
'''
    
    if current_app.debug or current_app.testing:
        # Log email content in development/testing mode
        print("\n------------------------")
        print("Password Reset Email")
        print("------------------------")
        print(f"To: {user.email}")
        print(f"Subject: {msg.subject}")
        print("Body:")
        print(msg.body)
        print("------------------------\n")
    else:
        # Actually send the email in production
        mail.send(msg) 