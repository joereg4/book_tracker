# Development Setup Guide

This guide will help you set up your development environment for the Book Tracker application.

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Git
- SQLite 3
- A text editor or IDE (VS Code recommended)
- Google Books API key

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

2. Set up Full Text Search:
```bash
python rebuild_fts_search.py
```

## Running Tests

1. Run all tests:
```bash
pytest
```

2. Run specific test file:
```bash
pytest tests/test_books.py
```

3. Run with coverage:
```bash
pytest --cov=.
```

Note: Tests use an in-memory SQLite database and will never affect your development or production database.

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
python backup_db.py
```

4. Restore database:
```bash
python restore_db.py
```

### Testing Email Functionality

In development, emails are captured and printed to the console by default. To test with a real SMTP server:

1. Configure email settings in `.env`
2. Restart the development server
3. Test password reset or email verification features

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
   - Ensure migrations are up to date
   - Check database file permissions
   - Verify SQLite version

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