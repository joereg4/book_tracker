"""Add reset token fields

Revision ID: add_reset_token_fields
Revises: 
Create Date: 2024-03-14 17:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_reset_token_fields'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Create a temporary table with the new schema
    op.execute('''
        CREATE TABLE users_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(80) NOT NULL UNIQUE,
            email VARCHAR(120) NOT NULL UNIQUE,
            password VARCHAR(200) NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            reset_token VARCHAR(100) UNIQUE,
            reset_token_expiry DATETIME
        )
    ''')
    
    # Copy data from the old table to the new table
    op.execute('''
        INSERT INTO users_new (id, username, email, password, created_at)
        SELECT id, username, email, password, created_at
        FROM users
    ''')
    
    # Drop the old table
    op.execute('DROP TABLE users')
    
    # Rename the new table to the original name
    op.execute('ALTER TABLE users_new RENAME TO users')

def downgrade():
    # Create a temporary table with the old schema
    op.execute('''
        CREATE TABLE users_old (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(80) NOT NULL UNIQUE,
            email VARCHAR(120) NOT NULL UNIQUE,
            password VARCHAR(128) NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Copy data back, excluding the new columns
    op.execute('''
        INSERT INTO users_old (id, username, email, password, created_at)
        SELECT id, username, email, password, created_at
        FROM users
    ''')
    
    # Drop the new table
    op.execute('DROP TABLE users')
    
    # Rename the old table back to the original name
    op.execute('ALTER TABLE users_old RENAME TO users') 