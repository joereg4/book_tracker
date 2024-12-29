import click
from flask.cli import with_appcontext
from utils.email_service import send_email

@click.group()
def email_cli():
    """Email management commands"""
    pass

@email_cli.command()
@click.argument('recipient')
@with_appcontext
def test(recipient):
    """Send a test email to verify configuration"""
    success = send_email(
        'Test Email from Book Tracker',
        recipient,
        'test_email',
        name=recipient.split('@')[0]
    )
    
    if success:
        click.echo(f"Test email sent to {recipient}")
    else:
        click.echo("Failed to send test email", err=True)
        raise click.ClickException("Email sending failed")

def init_app(app):
    """Register CLI commands"""
    app.cli.add_command(email_cli) 