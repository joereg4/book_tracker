from flask import Flask
from extensions import mail
from utils.email_service import send_email
from dotenv import load_dotenv

# Load development environment variables
load_dotenv('.env.development')

app = Flask(__name__)

# Override mail settings to use Docker ports
app.config.update(
    MAIL_SERVER='localhost',
    MAIL_PORT=1026,  # MailHog SMTP port in Docker
    MAIL_USE_TLS=False,
    MAIL_USERNAME=None,
    MAIL_PASSWORD=None,
    MAIL_DEFAULT_SENDER='noreply@dev-mail.readkeeper.com'
)

# Initialize mail extension
mail.init_app(app)

with app.app_context():
    # Test welcome email
    success = send_email(
        subject="Welcome to ReadKeeper",
        recipient="newuser@example.com",
        template="welcome",
        name="New User"
    )
    
    if success:
        print("Welcome email sent successfully!")
    else:
        print("Failed to send welcome email. Check the logs for details.")

    # Test password reset email
    success = send_email(
        subject="Reset Your ReadKeeper Password",
        recipient="user@example.com",
        template="password_reset",
        name="Test User",
        reset_url="http://localhost:5000/reset-password?token=test-token"
    )
    
    if success:
        print("Password reset email sent successfully!")
    else:
        print("Failed to send password reset email. Check the logs for details.")

    print("\nCheck MailHog at http://localhost:8025 to view both emails") 