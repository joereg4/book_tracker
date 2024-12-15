# Database Schema Documentation

## Overview

The Book Tracker application uses SQLite with SQLAlchemy ORM. The database schema includes tables for users, books, and full-text search functionality.

## Tables

### Users

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(64) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(128) NOT NULL,
    created_at DATETIME NOT NULL,
    last_seen DATETIME,
    reset_token VARCHAR(100),
    reset_token_expiry DATETIME
);
```

Fields:
- `id`: Unique identifier
- `username`: User's display name
- `email`: User's email address (used for login and notifications)
- `password_hash`: Hashed password using Werkzeug's security functions
- `created_at`: Account creation timestamp
- `last_seen`: Last activity timestamp
- `reset_token`: Password reset token
- `reset_token_expiry`: Reset token expiration timestamp

### Books

```sql
CREATE TABLE books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(200) NOT NULL,
    authors VARCHAR(200),
    google_books_id VARCHAR(20),
    isbn_10 VARCHAR(10),
    isbn_13 VARCHAR(13),
    publication_date DATE,
    page_count INTEGER,
    thumbnail_url VARCHAR(300),
    description TEXT,
    categories VARCHAR(200),
    status VARCHAR(20) NOT NULL,
    created_at DATETIME NOT NULL,
    date_read DATETIME,
    user_id INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);
```

Fields:
- `id`: Unique identifier
- `title`: Book title
- `authors`: Comma-separated list of authors
- `google_books_id`: Google Books API identifier
- `isbn_10`: ISBN-10 number
- `isbn_13`: ISBN-13 number
- `publication_date`: Book publication date
- `page_count`: Number of pages
- `thumbnail_url`: URL to book cover image
- `description`: Book description
- `categories`: Comma-separated list of categories
- `status`: Reading status (to_read, reading, read)
- `created_at`: When book was added to library
- `date_read`: When book was marked as read
- `user_id`: Foreign key to users table

### Full Text Search

```sql
CREATE VIRTUAL TABLE books_fts USING fts5(
    title,
    authors,
    description,
    categories,
    content='books',
    content_rowid='id'
);
```

Fields indexed for search:
- `title`: Book title
- `authors`: Book authors
- `description`: Book description
- `categories`: Book categories

## Relationships

### One-to-Many
- User → Books: One user can have many books
- Books are automatically deleted when user is deleted (CASCADE)

## Indexes

```sql
CREATE INDEX ix_books_user_id ON books (user_id);
CREATE INDEX ix_books_status ON books (status);
CREATE INDEX ix_books_google_books_id ON books (google_books_id);
CREATE UNIQUE INDEX ix_users_email ON users (email);
CREATE UNIQUE INDEX ix_users_username ON users (username);
```

## Full Text Search

The application uses SQLite's FTS5 module for full-text search capabilities:

1. **Triggers**: Automatically keep FTS index in sync with books table
2. **Search**: Uses SQLite's match operator for efficient text search
3. **Ranking**: Results ordered by relevance using bm25 algorithm

### Search Example
```sql
SELECT books.*
FROM books
JOIN books_fts ON books.id = books_fts.rowid
WHERE books_fts MATCH 'python programming'
ORDER BY rank;
```

## Database Management

### Backup
- Automatic backups created by `backup_db.py`
- Backups stored in `backups/` directory
- Filename format: `books_backup_YYYYMMDD_HHMMSS.db`

### Restore
- Use `restore_db.py` to restore from backup
- Creates safety backup before restore
- Verifies database integrity after restore

### Migrations
- Managed using Flask-Migrate
- Migration files in `migrations/versions/`
- Run with `flask db upgrade`

## Best Practices

1. **Data Integrity**
   - Use foreign key constraints
   - Implement cascading deletes
   - Validate data before insertion

2. **Performance**
   - Use appropriate indexes
   - Optimize queries for FTS
   - Regular VACUUM maintenance

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
results = Book.query.join(
    Book.fts,
    isouter=True
).filter(
    BookFTS.match('search term')
).all()
```

### Updating Status
```python
book = db.session.get(Book, book_id)
book.status = "read"
book.date_read = datetime.now()
db.session.commit()
```

## Troubleshooting

1. **FTS Not Working**
   - Run `rebuild_fts_search.py`
   - Check SQLite version supports FTS5
   - Verify triggers are in place

2. **Performance Issues**
   - Check indexes are being used
   - Analyze query plans
   - Consider database optimization

3. **Data Integrity**
   - Use foreign key checks
   - Verify cascade behavior
   - Check constraint violations

## Further Reading

- [SQLite Documentation](https://sqlite.org/docs.html)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [FTS5 Documentation](https://sqlite.org/fts5.html)
- [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/) 