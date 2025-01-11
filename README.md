# Book Tracker

A Flask web application for tracking your reading history and discovering new books using the Google Books API.

## Features

### Book Management
- Track books you've read, are reading, or want to read
- Search and discover new books via Google Books API
- Edit book details and refresh metadata
- Track reading dates for completed books
- Support for ISBN-10 and ISBN-13
- Automatic HTTPS conversion for book thumbnails

### Library Organization
- Categorize and organize your library
- Search within your library shelves using Full Text Search
- View book thumbnails and descriptions
- Smart shelf management system

### User Features
- Secure user authentication system
- Transactional email system (welcome emails, password resets)
- Profile management
- Export library data (CSV/JSON formats)
- Customizable user settings

### Analytics
- View reading statistics and trends
- Track reading progress
- Analyze reading patterns
- Category and author statistics

### Security Features
- Rate limiting protection (Redis-backed)
- CSRF protection
- Secure password handling
- Email verification system
- Database backup and restore utilities

### Development Features
- Docker-based development environment
- MailHog for email testing
- Redis for rate limiting
- Comprehensive test suite
- Development/Production environment separation

## Prerequisites
- Python 3.8+
- pip (Python package installer)
- Google Books API key
- Docker and Docker Compose (for development environment)

## Setup

### Getting a Google Books API Key

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Books API:
   - Go to "APIs & Services" → "Library"
   - Search for "Books API"
   - Click "Enable"
4. Create credentials:
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "API Key"
   - Copy your API key

### Installation

1. Clone the repository:
```bash
git clone https://github.com/joereg4/book_tracker.git
cd book-tracker
```

2. Check Python version:
```bash
python --version
```   

3. Create and activate a virtual environment:
```bash
python -m venv books
# On Windows:
books\Scripts\activate
# On macOS/Linux:
source books/bin/activate
```

4. Install dependencies:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Development Environment

1. Start the development services (email and Redis):
```bash
docker-compose up -d
```

This will start:
- MailHog (SMTP server for development)
  - SMTP: localhost:1026
  - Web UI: http://localhost:8025
- Redis (for rate limiting)
  - localhost:6379

2. Create a `.env.development` file:
```plaintext
# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=1
FLASK_SECRET_KEY=dev-secret-key-change-in-production

# Database Configuration
DATABASE_URL=sqlite:///dev.db

# Email Configuration (MailHog for development)
MAIL_SERVER=localhost
MAIL_PORT=1026
MAIL_USE_TLS=False
MAIL_USERNAME=
MAIL_PASSWORD=
MAIL_DEFAULT_SENDER=noreply@dev-mail.readkeeper.com

# Rate Limiting
REDIS_URL=redis://localhost:6379
```

### Production Configuration

For production, create a `.env` file:
```plaintext
FLASK_SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(16))')
GOOGLE_BOOKS_API_KEY=your_google_books_api_key_here

# Email Configuration (Postfix)
MAIL_SERVER=localhost
MAIL_PORT=25
MAIL_USE_TLS=False
MAIL_USERNAME=noreply
MAIL_PASSWORD=your_secure_password
MAIL_DEFAULT_SENDER=noreply@your-domain.com

# Redis Configuration
REDIS_URL=redis://localhost:6379
```

### Testing Email Configuration

You can test the email configuration using the provided test script:
```bash
python test_smtp.py
```

This will send test emails (welcome and password reset) that you can view in:
- Development: MailHog web interface (http://localhost:8025)
- Production: Your configured SMTP server

### Configuration

1. Create a `.env` file in the project root (see `.env example` for template):
```plaintext
FLASK_SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(16))')
GOOGLE_BOOKS_API_KEY=your_google_books_api_key_here
MAIL_SERVER=smtp.gmail.com  # Optional: for email functionality
MAIL_PORT=587              # Optional: for email functionality
MAIL_USERNAME=your_email   # Optional: for email functionality
MAIL_PASSWORD=your_password # Optional: for email functionality
```

2. Initialize the database:
```bash
flask db upgrade
python rebuild_fts_search.py  # Initialize full-text search
```

3. Set up admin user:
```bash
# Make an existing user an admin
flask users make-admin <username>

# List all admin users
flask users list-admins

# Remove admin privileges
flask users remove-admin <username>
```

4. Run the application:
```bash
python app.py
```

The application will be available at `http://127.0.0.1:5000`

## Usage

### Account Management
1. **Sign Up and Login**
   - Create a new account with email verification
   - Secure password reset functionality if needed
   - Profile customization options

2. **Security Features**
   - Rate limiting prevents brute force attempts
   - CSRF protection on all forms
   - Secure session handling

### Book Management
1. **Adding Books**
   - Search using the Google Books API
   - Select shelf (To Read, Currently Reading, or Read)
   - Automatic metadata population

2. **Managing Your Library**
   - Move books between shelves
   - Edit book details with Google Books refresh option
   - Track reading dates
   - Full text search within your library
   - Export library data in CSV or JSON format

3. **Book Details**
   - Comprehensive information including:
     - Title and authors
     - Publication details
     - Page count
     - Description (HTML-free)
     - Categories
     - ISBN numbers
     - Language and maturity rating
     - Preview and info links
     - Book thumbnails

### Analytics
1. **Reading Statistics**
   - Track reading progress
   - View completion trends
   - Analyze reading patterns
   - Category distribution
   - Author statistics

### Data Management
1. **Backup and Restore**
   - Automatic database backups
   - Restore functionality
   - Data export options

## Development

See the [Contributing Guide](CONTRIBUTING.md) for detailed development instructions.

### Key Development Features
- Comprehensive test suite
- Database migration system
- Development email capture
- Rate limiting configuration
- Blueprint-based architecture

## Security

See [SECURITY.md](SECURITY.md) for security policy and reporting vulnerabilities.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed contribution guidelines.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

# Email Configuration

Email functionality is optional in development (defaults to console output) but required for production. The application uses Gmail OAuth2 for secure email handling.

1. Development Setup:
```bash
# Configure email in .env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your_email@gmail.com
MAIL_USE_OAUTH2=True
MAIL_OAUTH_CLIENT_ID=your_oauth_client_id
MAIL_OAUTH_CLIENT_SECRET=your_oauth_client_secret
MAIL_DEFAULT_SENDER=noreply@yourdomain.com

# Test email configuration
flask email-cli test test@example.com
```

2. Gmail OAuth2 Setup:
- Go to Google Cloud Console
- Create a new project or select existing one
- Enable Gmail API
- Configure OAuth2 consent screen
- Create OAuth2 credentials (Web application type)
- Add authorized redirect URIs
- Use the client ID and client secret in your .env file

3. Production Setup:
- Set FLASK_ENV=production
- Configure OAuth2 credentials
- Test email delivery
- Monitor email logs

See [Email Configuration Guide](docs/development/setup.md#testing-email-functionality) for detailed setup instructions.
```
