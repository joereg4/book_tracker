"""add admin and last seen

Revision ID: 5a42a219a910
Revises: add_reset_token_fields
Create Date: 2024-12-15 10:00:21.123456

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5a42a219a910'
down_revision = 'add_reset_token_fields'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('users') as batch_op:
        batch_op.add_column(sa.Column('is_admin', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('last_seen', sa.DateTime(), nullable=True))
    
    # Set default values
    op.execute('UPDATE users SET is_admin = 0 WHERE is_admin IS NULL')
    op.execute('UPDATE users SET last_seen = created_at WHERE last_seen IS NULL')
    
    # Make columns non-nullable with defaults
    with op.batch_alter_table('users') as batch_op:
        batch_op.alter_column('is_admin',
                            existing_type=sa.Boolean(),
                            nullable=False,
                            server_default=sa.text('0'))
        batch_op.alter_column('last_seen',
                            existing_type=sa.DateTime(),
                            nullable=False,
                            server_default=sa.text('CURRENT_TIMESTAMP'))


def downgrade():
    with op.batch_alter_table('users') as batch_op:
        batch_op.drop_column('last_seen')
        batch_op.drop_column('is_admin')
