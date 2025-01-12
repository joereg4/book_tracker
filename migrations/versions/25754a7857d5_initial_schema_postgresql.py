"""initial_schema_postgresql

Revision ID: 25754a7857d5
Revises: 
Create Date: 2024-12-29 09:07:11.478098

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '25754a7857d5'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create the FTS configuration
    op.execute("""
        CREATE EXTENSION IF NOT EXISTS unaccent;
        DROP TEXT SEARCH CONFIGURATION IF EXISTS books_fts_config;
        CREATE TEXT SEARCH CONFIGURATION books_fts_config (COPY = english);
        ALTER TEXT SEARCH CONFIGURATION books_fts_config
            ALTER MAPPING FOR hword, hword_part, word
            WITH unaccent, english_stem;
    """)
    
    # Create users table
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=64), nullable=False),
        sa.Column('email', sa.String(length=120), nullable=False),
        sa.Column('password', sa.String(length=200), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('is_admin', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('last_seen', sa.DateTime(), nullable=True),
        sa.Column('reset_token', sa.String(length=100), nullable=True),
        sa.Column('reset_token_expiry', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    
    # Create books table
    op.create_table('books',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('authors', sa.String(length=200), nullable=False),
        sa.Column('isbn', sa.String(length=13), nullable=True),
        sa.Column('isbn13', sa.String(length=13), nullable=True),
        sa.Column('published_date', sa.String(length=10), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('date_read', sa.DateTime(), nullable=True),
        sa.Column('google_books_id', sa.String(length=20), nullable=True),
        sa.Column('etag', sa.String(length=50), nullable=True),
        sa.Column('self_link', sa.String(length=250), nullable=True),
        sa.Column('publisher', sa.String(length=100), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('page_count', sa.Integer(), nullable=True),
        sa.Column('print_type', sa.String(length=20), nullable=True),
        sa.Column('categories', sa.String(length=100), nullable=True),
        sa.Column('maturity_rating', sa.String(length=20), nullable=True),
        sa.Column('language', sa.String(length=10), nullable=True),
        sa.Column('preview_link', sa.String(length=250), nullable=True),
        sa.Column('info_link', sa.String(length=250), nullable=True),
        sa.Column('canonical_volume_link', sa.String(length=250), nullable=True),
        sa.Column('small_thumbnail', sa.String(length=250), nullable=True),
        sa.Column('thumbnail', sa.String(length=250), nullable=True),
        sa.Column('content_version', sa.String(length=20), nullable=True),
        sa.Column('is_ebook', sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Add the search vector column and index
    op.execute("""
        ALTER TABLE books 
        ADD COLUMN search_vector tsvector 
        GENERATED ALWAYS AS (
            setweight(to_tsvector('books_fts_config', coalesce(title, '')), 'A') ||
            setweight(to_tsvector('books_fts_config', coalesce(authors, '')), 'B') ||
            setweight(to_tsvector('books_fts_config', coalesce(description, '')), 'C') ||
            setweight(to_tsvector('books_fts_config', coalesce(categories, '')), 'D')
        ) STORED;
        
        CREATE INDEX books_search_idx ON books USING GIN (search_vector);
    """)


def downgrade():
    # Drop tables
    op.drop_table('books')
    op.drop_table('users')
    
    # Drop FTS configuration
    op.execute("""
        DROP INDEX IF EXISTS books_search_idx;
        DROP TEXT SEARCH CONFIGURATION IF EXISTS books_fts_config;
    """)
