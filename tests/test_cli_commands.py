from click.testing import CliRunner
from models import User, db
from werkzeug.security import generate_password_hash
from cli.user_commands import users_cli
from cli.email_commands import email_cli

def test_make_admin_command(app, db_session):
    """Test make-admin CLI command"""
    runner = CliRunner()
    
    # Create test user
    user = User(
        username='testuser',
        email='test@example.com',
        password=generate_password_hash('testpass123')
    )
    db_session.add(user)
    db_session.commit()
    
    # Run command
    result = runner.invoke(users_cli, ['make-admin', 'testuser'])
    assert result.exit_code == 0
    assert "Successfully made testuser an admin" in result.output
    
    # Verify user is admin
    user = db_session.get(User, user.id)
    assert user.is_admin is True

def test_make_admin_nonexistent_user(app, db_session):
    """Test make-admin command with nonexistent user"""
    runner = CliRunner()
    result = runner.invoke(users_cli, ['make-admin', 'nonexistent'])
    assert result.exit_code == 0
    assert "Error: User nonexistent not found" in result.output

def test_remove_admin_command(app, db_session):
    """Test remove-admin CLI command"""
    runner = CliRunner()
    
    # Create admin user
    user = User(
        username='adminuser',
        email='admin@example.com',
        password=generate_password_hash('testpass123'),
        is_admin=True
    )
    db_session.add(user)
    db_session.commit()
    
    # Run command
    result = runner.invoke(users_cli, ['remove-admin', 'adminuser'])
    assert result.exit_code == 0
    assert "Successfully removed admin privileges from adminuser" in result.output
    
    # Verify user is no longer admin
    user = db_session.get(User, user.id)
    assert user.is_admin is False

def test_list_admins_command(app, db_session):
    """Test list-admins CLI command"""
    runner = CliRunner()
    
    # Create mix of admin and non-admin users
    users = [
        User(
            username=f'user{i}',
            email=f'user{i}@example.com',
            password=generate_password_hash('testpass123'),
            is_admin=i < 2  # First two users are admins
        )
        for i in range(4)
    ]
    db_session.add_all(users)
    db_session.commit()
    
    # Run command
    result = runner.invoke(users_cli, ['list-admins'])
    assert result.exit_code == 0
    assert "Admin users:" in result.output
    assert "user0" in result.output
    assert "user1" in result.output
    assert "user2" not in result.output
    assert "user3" not in result.output

def test_list_admins_no_admins(app, db_session):
    """Test list-admins command when no admins exist"""
    runner = CliRunner()
    result = runner.invoke(users_cli, ['list-admins'])
    assert result.exit_code == 0
    assert "No admin users found" in result.output

def test_email_test_command(app, db_session, monkeypatch):
    """Test email test CLI command"""
    runner = CliRunner()
    
    # Mock send_email function
    def mock_send_email(*args, **kwargs):
        return True
    
    from utils import email_service
    monkeypatch.setattr(email_service, 'send_email', mock_send_email)
    
    # Run command
    result = runner.invoke(email_cli, ['test', 'test@example.com'])
    assert result.exit_code == 0
    assert "Test email sent to test@example.com" in result.output

def test_email_test_command_failure(app, db_session, monkeypatch):
    """Test email test CLI command when email fails"""
    runner = CliRunner()
    
    # Disable development mode
    app.config['MAIL_SUPPRESS_SEND'] = False
    
    # Mock mail.send to raise an exception
    def mock_send(*args, **kwargs):
        raise Exception("Failed to send email")
    
    from extensions import mail
    monkeypatch.setattr(mail, 'send', mock_send)
    
    # Run command
    result = runner.invoke(email_cli, ['test', 'test@example.com'])
    assert result.exit_code == 1  # Command should fail
    assert "Failed to send test email" in result.output
    assert "Email sending failed" in result.output 