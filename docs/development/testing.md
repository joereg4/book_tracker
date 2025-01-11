# Testing Guide

## Overview

The Book Tracker application uses pytest for testing. The test suite includes unit tests, integration tests, and functional tests, with special attention to database safety and security features.

## Test Structure

```
tests/
├── conftest.py              # Test configuration and fixtures
├── test_admin.py           # Admin functionality tests
├── test_auth.py            # Authentication tests
├── test_books.py           # Book management tests
├── test_cli_commands.py    # CLI command tests
├── test_email.py           # Email functionality tests
├── test_main.py            # Main routes tests
├── test_monitoring.py      # Rate limiting and monitoring tests
├── test_password_reset.py  # Password reset functionality tests
├── test_profile.py         # User profile tests
├── test_reset_flow.py      # End-to-end reset flow tests
├── test_security.py        # Security feature tests
├── test_shelf.py           # Shelf management tests
└── test_stats.py          # Statistics tests
```

## Test Environment Setup

1. Start the test environment:
```bash
docker-compose up -d
```

This provides:
- MailHog for email testing
- Redis for rate limiting tests

2. Verify services are running:
```bash
docker-compose ps
```

## Running Tests

### Basic Test Execution

Run all tests:
```bash
python -m pytest tests/
```

Run specific test file:
```bash
python -m pytest tests/test_email.py
```

Run specific test:
```bash
python -m pytest tests/test_email.py::test_welcome_email
```

### Test Coverage

Run tests with coverage:
```bash
python -m pytest --cov=.
```

Generate HTML coverage report:
```bash
python -m pytest --cov=. --cov-report=html
```

## Email Testing

### Test Configuration
- Tests use a mocked email sender by default
- Email templates are tested without actually sending emails
- MailHog is available for manual testing

### Manual Email Testing
1. Start MailHog:
```bash
docker-compose up -d mailhog
```

2. Send test email:
```bash
python test_smtp.py
```

3. View emails:
- Open http://localhost:8025 in your browser
- All sent emails will be captured here

### Email Test Cases
- Welcome emails
- Password reset emails
- Test emails
- Error cases (missing templates, server errors)

## Test Database

- Tests use SQLite in-memory database
- Each test gets a fresh database
- Full Text Search is configured if using PostgreSQL

## Fixtures

Key fixtures in `conftest.py`:
- `app`: Flask application instance
- `db_session`: Database session
- `client`: Test client
- `test_user`: Sample user
- `test_book`: Sample book
- `mail`: Email testing configuration
- `redis_client`: Fake Redis for rate limiting tests

## Mocking

The test suite uses various mocks:
- Email sending (`mock_mail_send`)
- Redis client (`FakeRedis`)
- Rate limiting storage
- External API calls 