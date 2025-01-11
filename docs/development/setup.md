# Development Setup Guide

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Git
- PostgreSQL 12 or higher
- A text editor or IDE (VS Code recommended)
- Google Books API key
- Docker and Docker Compose
- Redis (optional, for rate limiting)

## Initial Setup

1. Clone the repository:
```bash
git clone https://github.com/joereg4/book_tracker.git
cd book-tracker
```

2. Create and activate virtual environment:
```bash
python -m venv books
# On Windows:
books\Scripts\activate
# On macOS/Linux:
source books/bin/activate
```

3. Install dependencies:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

4. Start development services:
```bash
docker-compose up -d
```

This will start:
- MailHog (email testing service)
  - SMTP: localhost:1026
  - Web UI: http://localhost:8025
- Redis (for rate limiting)
  - localhost:6379

5. Create a `.env.development` file:
```bash
cp .env.example .env.development
```

6. Configure your environment variables in `.env.development`:
```plaintext
# Flask Configuration
FLASK_SECRET_KEY=dev-secret-key-change-in-production
FLASK_ENV=development
FLASK_DEBUG=1

# Database Configuration
DATABASE_URL=sqlite:///dev.db  # or your PostgreSQL URL

# Email Configuration (MailHog)
MAIL_SERVER=localhost
MAIL_PORT=1026
MAIL_USE_TLS=False
MAIL_USERNAME=
MAIL_PASSWORD=
MAIL_DEFAULT_SENDER=noreply@dev-mail.readkeeper.com

# Rate Limiting
REDIS_URL=redis://localhost:6379
```

## Testing Email Functionality

1. Send a test email:
```bash
python test_smtp.py
```

2. View sent emails in MailHog:
   - Open http://localhost:8025 in your browser
   - All emails sent during development will be captured here

## Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_email.py

# Run with verbose output
python -m pytest -v tests/
```

## Development Workflow

1. Start development services:
```bash
docker-compose up -d
```

2. Run the application:
```bash
flask run
```

3. Access the application:
   - Web UI: http://localhost:5000
   - MailHog: http://localhost:8025

4. Stop development services:
```bash
docker-compose down
```

## PostgreSQL Setup

1. Install PostgreSQL:
```bash
# macOS (using Homebrew)
brew install postgresql@15
brew services start postgresql@15

# Ubuntu/Debian
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib
```

2. Create database and user:
```bash
createdb books
```

## Configuration

1. Create `.env` file:
```bash
cp .env.example .env
```

2. Configure environment variables in `.env`:
```plaintext
FLASK_SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(16))')
GOOGLE_BOOKS_API_KEY=your_api_key_here
FLASK_ENV=development
FLASK_DEBUG=1

# Database URL (update username and password if needed)
DATABASE_URL=postgresql://localhost/books

# Optional email settings (defaults to console in development)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your_email
MAIL_PASSWORD=your_password
```

## Database Setup

1. Initialize the database:
```bash
flask db upgrade
```

This will:
- Create all tables
- Set up full-text search configuration
- Create necessary indexes

## Development Server

1. Start the development server:
```bash
python app.py
```

2. Access the application:
```
http://127.0.0.1:5000
```

## Development Tools

### Flask CLI

Useful Flask CLI commands:
```bash
flask routes  # List all routes
flask db upgrade  # Run migrations
flask shell  # Start Python shell with app context
```

### Database Management

1. Create new migration:
```bash
flask db migrate -m "Description of changes"
```

2. Apply migrations:
```bash
flask db upgrade
```

3. Backup database:
```bash
pg_dump books > backup.sql
```

4. Restore database:
```bash
psql books < backup.sql
```

## Code Style

The project follows PEP 8 guidelines. Key points:
- Use 4 spaces for indentation
- Maximum line length of 79 characters
- Use meaningful variable names
- Add docstrings to functions and classes

## Git Workflow

1. Create a feature branch:
```bash
git checkout -b feature-name
```

2. Make changes and commit:
```bash
git add .
git commit -m "Descriptive commit message"
```

3. Push changes:
```bash
git push origin feature-name
```

4. Create pull request on GitHub

## Troubleshooting

### Common Issues

1. **Database Errors**
   - Ensure PostgreSQL service is running
   - Check database connection settings
   - Verify database user permissions
   - Run migrations

2. **Email Issues**
   - Check SMTP settings
   - Verify email credentials
   - Review console output in development

3. **Test Failures**
   - Ensure virtual environment is active
   - Verify all dependencies are installed
   - Check test database configuration

### Getting Help

1. Check existing documentation
2. Search GitHub issues
3. Create a new issue with:
   - Error message
   - Steps to reproduce
   - Expected behavior
   - Environment details

## Next Steps

- Review [Project Structure](structure.md)
- Read [Testing Guide](testing.md)
- Check [Configuration Guide](configuration.md)
- See [Contributing Guidelines](../../CONTRIBUTING.md) 