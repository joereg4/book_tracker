import click
from flask.cli import with_appcontext
from models import User, db

@click.group()
def users_cli():
    """User management commands."""
    pass

@users_cli.command()
@click.argument('username')
@with_appcontext
def make_admin(username):
    """Make a user an admin by username."""
    user = User.query.filter_by(username=username).first()
    if user is None:
        click.echo(f'Error: User {username} not found')
        return
    user.is_admin = True
    db.session.commit()
    click.echo(f'Successfully made {username} an admin')

@users_cli.command()
@click.argument('username')
@with_appcontext
def remove_admin(username):
    """Remove admin privileges from a user by username."""
    user = User.query.filter_by(username=username).first()
    if user is None:
        click.echo(f'Error: User {username} not found')
        return
    user.is_admin = False
    db.session.commit()
    click.echo(f'Successfully removed admin privileges from {username}')

@users_cli.command()
@with_appcontext
def list_admins():
    """List all admin users."""
    admins = User.query.filter_by(is_admin=True).all()
    if not admins:
        click.echo('No admin users found')
        return
    click.echo('Admin users:')
    for admin in admins:
        click.echo(f'- {admin.username} ({admin.email})')

def init_app(app):
    """Register CLI commands"""
    app.cli.add_command(users_cli) 