# Development Setup Guide

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Git
- PostgreSQL 12 or higher
- A text editor or IDE (VS Code recommended)
- Google Books API key
- Redis (optional, for rate limiting)
- Gmail account (for email functionality)

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

4. Create a `.env` file from the example:
```bash
cp .env.example .env
```

5. Configure your environment variables in `.env`:
```plaintext
# Flask configuration
FLASK_SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(16))')
APP_URL=http://localhost:5000
FLASK_ENV=development
FLASK_DEBUG=1

# Database configuration
DATABASE_URL=postgresql://localhost/books

# Google Books API
GOOGLE_BOOKS_API_KEY=your_google_books_api_key_here

# OAuth2 Configuration
GOOGLE_OAUTH_CLIENT_ID=your_oauth_client_id
GOOGLE_OAUTH_CLIENT_SECRET=your_oauth_client_secret
GOOGLE_OAUTH_REDIRECT_URI=http://localhost:5000/oauth2callback

# Email Configuration
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your_email@gmail.com
MAIL_USE_OAUTH2=True
MAIL_DEFAULT_SENDER=noreply@yourdomain.com
```

6. Set up OAuth2 credentials:
   - Go to [Google Cloud Console](https://console.cloud.google.com)
   - Create a new project or select existing one
   - Enable Gmail API and Google Books API
   - Configure OAuth2 consent screen
   - Create OAuth2 credentials (Web application type)
   - Add authorized redirect URIs
   - Copy credentials to your `.env` file

6. Initialize the database:
```bash
flask db upgrade
```

## Email Configuration

### Development Mode
For development, emails are suppressed by default and logged to the console. To test actual email sending:

1. Set `MAIL_SUPPRESS_SEND=False` in your `.env` file
2. Configure Gmail OAuth2 credentials:
   - Create a project in Google Cloud Console
   - Enable Gmail API
   - Create OAuth2 credentials
   - Add authorized redirect URIs
   - Update `.env` with OAuth2 settings:
     ```plaintext
     MAIL_USE_OAUTH2=True
     MAIL_USERNAME=your-email@gmail.com
     MAIL_DEFAULT_SENDER=your-email@gmail.com
     MAIL_OAUTH_CLIENT_ID=your-oauth-client-id
     MAIL_OAUTH_CLIENT_SECRET=your-oauth-client-secret
     MAIL_OAUTH_REDIRECT_URI=http://localhost:5000/oauth2callback
     ```

### Testing Email Functionality

1. Run the email test command:
```bash
flask email-cli test your-email@example.com
```

2. Follow the authorization flow:
   - Click the authorization URL in the console
   - Sign in with your Gmail account
   - Grant permissions
   - Copy the code from the redirect URL
   - Run: `flask email-cli authorize <code>`

3. The test email should be sent to your specified address

### Production Setup
For production:
1. Set `FLASK_ENV=production`
2. Set `MAIL_SUPPRESS_SEND=False`
3. Configure OAuth2 with production credentials
4. Use a production domain for redirect URIs

## Running Tests

1. Run all tests:
```bash
pytest
```

2. Run specific test file:
```bash
pytest tests/test_email.py
```

3. Run with coverage:
```bash
pytest --cov=.
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