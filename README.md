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
- Password reset via email
- Profile management
- Export library data (CSV/JSON formats)
- Customizable user settings

### Analytics
- View reading statistics and trends
- Track reading progress
- Analyze reading patterns
- Category and author statistics

### Security Features
- Rate limiting protection
- CSRF protection
- Secure password handling
- Email verification system
- Database backup and restore utilities

## Prerequisites
- Python 3.8+
- pip (Python package installer)
- Google Books API key
- SMTP server for email functionality (optional, defaults to console output in development)

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

3. Run the application:
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
```
