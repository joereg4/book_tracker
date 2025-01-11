from flask import Flask
from flask_mail import Mail, Message
from dotenv import load_dotenv
import os

# Load development environment variables
load_dotenv('.env.development')

app = Flask(__name__)

# Configure Flask-Mail with MailHog's default SMTP port
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
    try:
        msg = Message(
            subject="Test Email from ReadKeeper",
            recipients=["test@example.com"],
            body="This is a test email from the ReadKeeper development environment."
        )
        mail.send(msg)
        print("Test email sent successfully!")
        print("Check MailHog at http://localhost:8025 to view the email")
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        print("Make sure MailHog is running and accessible at localhost:1026") 