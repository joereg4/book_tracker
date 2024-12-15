"""Add reset token fields and is_admin column

Revision ID: add_reset_token_fields
Revises: 
Create Date: 2024-03-14 17:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column

# revision identifiers, used by Alembic.
revision = 'add_reset_token_fields'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Add is_admin column
    op.add_column('users', sa.Column('is_admin', sa.Boolean(), nullable=True))
    op.execute('UPDATE users SET is_admin = 0 WHERE is_admin IS NULL')
    op.alter_column('users', 'is_admin', nullable=False, server_default=sa.text('0'))
    
    # Add last_seen column
    op.add_column('users', sa.Column('last_seen', sa.DateTime(), nullable=True))
    op.execute('UPDATE users SET last_seen = created_at WHERE last_seen IS NULL')
    op.alter_column('users', 'last_seen', nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'))

def downgrade():
    # Remove added columns
    op.drop_column('users', 'last_seen')
    op.drop_column('users', 'is_admin') 