# Book Tracker

A Flask web application for tracking your reading history and discovering new books using the Google Books API.

## Features
- Track books you've read, are reading, or want to read
- Search and discover new books via Google Books API
- View reading statistics and trends
- Categorize and organize your library
- Edit book details and refresh metadata
- Search within your library shelves
- View book thumbnails and descriptions
- Track reading dates for completed books
- Support for ISBN-10 and ISBN-13
- Automatic HTTPS conversion for book thumbnails

## Prerequisites
- Python 3.8+
- pip (Python package installer)
- Google Books API key

## Getting a Google Books API Key

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

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/book-tracker.git
cd book-tracker

2. Create and activate a virtual environment:
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root:
```plaintext
FLASK_SECRET_KEY=your_secret_key_here
GOOGLE_BOOKS_API_KEY=your_google_books_api_key_here
```

5. Run the application:
```bash
python app.py
```

The application will automatically create the database on first run.

The application will be available at `http://127.0.0.1:5000`

## Usage

1. **Adding Books**
   - Search for books using the Google Books API
   - Select a shelf (To Read, Currently Reading, or Read)
   - Books are automatically populated with metadata from Google Books

2. **Managing Books**
   - Move books between shelves using the dropdown menu
   - Edit book details with option to refresh from Google Books
   - Track reading dates for completed books
   - Remove books from your library
   - Search within your library shelves

3. **Book Details**
   - View comprehensive book information including:
     - Title and authors
     - Publication date and publisher
     - Page count
     - Description (HTML-free)
     - Categories
     - ISBN numbers
     - Language and maturity rating
     - Preview and info links
     - Book thumbnails

4. **Viewing Statistics**
   - See reading trends and patterns
   - Track categories and authors
   - Monitor reading progress

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
```
