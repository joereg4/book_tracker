# Database Schema Documentation

## Overview

The Book Tracker application uses PostgreSQL with SQLAlchemy ORM. The database schema includes tables for users, books, and built-in full-text search functionality.

## Tables

### Users

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(64) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password VARCHAR(128) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE,
    is_admin BOOLEAN NOT NULL DEFAULT FALSE,
    last_seen TIMESTAMP WITH TIME ZONE,
    reset_token VARCHAR(100),
    reset_token_expiry TIMESTAMP WITH TIME ZONE
);

CREATE UNIQUE INDEX ix_users_email ON users (email);
CREATE UNIQUE INDEX ix_users_username ON users (username);
```

Fields:
- `id`: Unique identifier (auto-incrementing)
- `username`: User's display name
- `email`: User's email address (used for login and notifications)
- `password`: Hashed password using Werkzeug's security functions
- `created_at`: Account creation timestamp
- `is_admin`: Boolean flag for admin privileges
- `last_seen`: Last activity timestamp
- `reset_token`: Password reset token
- `reset_token_expiry`: Reset token expiration timestamp

### Books

```sql
CREATE TABLE books (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    authors VARCHAR(200) NOT NULL,
    isbn VARCHAR(13),
    isbn13 VARCHAR(13),
    published_date VARCHAR(10),
    status VARCHAR(20) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    date_read TIMESTAMP WITH TIME ZONE,
    google_books_id VARCHAR(20),
    etag VARCHAR(50),
    self_link VARCHAR(250),
    publisher VARCHAR(100),
    description TEXT,
    page_count INTEGER,
    print_type VARCHAR(20),
    categories VARCHAR(100),
    maturity_rating VARCHAR(20),
    language VARCHAR(10),
    preview_link VARCHAR(250),
    info_link VARCHAR(250),
    canonical_volume_link VARCHAR(250),
    small_thumbnail VARCHAR(250),
    thumbnail VARCHAR(250),
    content_version VARCHAR(20),
    is_ebook BOOLEAN,
    search_vector tsvector GENERATED ALWAYS AS (
        setweight(to_tsvector('books_fts_config', coalesce(title, '')), 'A') ||
        setweight(to_tsvector('books_fts_config', coalesce(authors, '')), 'B') ||
        setweight(to_tsvector('books_fts_config', coalesce(description, '')), 'C') ||
        setweight(to_tsvector('books_fts_config', coalesce(categories, '')), 'D')
    ) STORED
);

CREATE INDEX books_search_idx ON books USING GIN (search_vector);
```

Fields:
- `id`: Unique identifier (auto-incrementing)
- `user_id`: Foreign key to users table
- `title`: Book title
- `authors`: Book authors
- `isbn`: ISBN-10 number
- `isbn13`: ISBN-13 number
- `published_date`: Book publication date
- `status`: Reading status (to_read, reading, read)
- `created_at`: When book was added to library
- `date_read`: When book was marked as read
- Additional fields from Google Books API
- `search_vector`: Generated column for full-text search

## Full Text Search

The application uses PostgreSQL's built-in full-text search capabilities:

1. **Configuration**: Custom text search configuration with unaccent support
```sql
CREATE TEXT SEARCH CONFIGURATION books_fts_config (COPY = english);
ALTER TEXT SEARCH CONFIGURATION books_fts_config
    ALTER MAPPING FOR hword, hword_part, word
    WITH unaccent, english_stem;
```

2. **Search Vector**: Generated column combining multiple fields with different weights
- Title (weight A)
- Authors (weight B)
- Description (weight C)
- Categories (weight D)

3. **Search Example**:
```sql
SELECT *
FROM books
WHERE search_vector @@ plainto_tsquery('books_fts_config', 'search terms')
ORDER BY ts_rank(search_vector, plainto_tsquery('books_fts_config', 'search terms')) DESC;
```

## Relationships

### One-to-Many
- User → Books: One user can have many books
- Books are automatically deleted when user is deleted (CASCADE)

## Database Management

### Backup
```bash
pg_dump books > backup.sql
```

### Restore
```bash
psql books < backup.sql
```

### Migrations
- Managed using Flask-Migrate
- Migration files in `migrations/versions/`
- Run with `flask db upgrade`

## Best Practices

1. **Data Integrity**
   - Use foreign key constraints
   - Implement cascading deletes
   - Use appropriate data types

2. **Performance**
   - Use GIN index for full-text search
   - Regular VACUUM ANALYZE
   - Monitor query performance

3. **Security**
   - Store only hashed passwords
   - Use parameterized queries
   - Regular backups

## Common Operations

### Adding a Book
```python
book = Book(
    title="Example Book",
    authors="Author Name",
    status="to_read",
    user_id=current_user.id
)
db.session.add(book)
db.session.commit()
```

### Searching Books
```python
from sqlalchemy import text
results = Book.query.filter(
    text("search_vector @@ plainto_tsquery('books_fts_config', :query)")
).params(query='search terms').all()
```

### Updating Status
```python
book = db.session.get(Book, book_id)
book.status = "read"
book.date_read = datetime.now(timezone.utc)
db.session.commit()
```

## Troubleshooting

1. **Search Issues**
   - Check text search configuration
   - Verify GIN index exists
   - Monitor search performance

2. **Performance Issues**
   - Check query plans with EXPLAIN ANALYZE
   - Update table statistics
   - Review index usage

3. **Data Integrity**
   - Check foreign key constraints
   - Verify timezone handling
   - Monitor transaction logs

## Further Reading

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [PostgreSQL Full Text Search](https://www.postgresql.org/docs/current/textsearch.html)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/) 