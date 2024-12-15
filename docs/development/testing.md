# Testing Guide

## Overview

The Book Tracker application uses pytest for testing. The test suite includes unit tests, integration tests, and functional tests, with special attention to database safety and security features.

## Test Structure

```
tests/
├── conftest.py              # Test configuration and fixtures
├── test_auth.py            # Authentication tests
├── test_books.py           # Book management tests
├── test_main.py            # Main routes tests
├── test_password_reset.py  # Password reset functionality tests
├── test_profile.py         # User profile tests
├── test_reset_flow.py      # End-to-end reset flow tests
├── test_security.py        # Security feature tests
├── test_shelf.py           # Shelf management tests
└── test_stats.py          # Statistics tests
```

## Running Tests

### Basic Test Execution

Run all tests:
```bash
pytest
```

Run specific test file:
```bash
pytest tests/test_books.py
```

Run specific test:
```bash
pytest tests/test_books.py::test_add_book
```

### Test Coverage

Run tests with coverage:
```bash
pytest --cov=.
```

Generate HTML coverage report:
```bash
pytest --cov=. --cov-report=html
```

## Test Configuration

### Database Safety

The test suite uses an in-memory SQLite database to ensure test isolation and protect production data:

```python
class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = True
    SECRET_KEY = 'test-secret-key-not-for-production'
    RATELIMIT_ENABLED = True
```

Safety measures:
1. In-memory database for all tests
2. Multiple safety checks in app configuration
3. Runtime verification of database URI
4. Automatic cleanup after each test

### Test Fixtures

Common fixtures in `conftest.py`:

```python
@pytest.fixture(scope='session')
def app():
    """Create test application"""
    test_app = create_app('config.TestConfig')
    return test_app

@pytest.fixture(scope='session')
def client(app):
    """Create test client"""
    return app.test_client()

@pytest.fixture(scope='function')
def db_session(app):
    """Create clean database session"""
    with app.app_context():
        db.drop_all()
        db.create_all()
        yield db.session
        db.session.remove()
```

## Writing Tests

### Test Categories

1. **Unit Tests**
   - Test individual functions/methods
   - Mock external dependencies
   - Focus on edge cases

2. **Integration Tests**
   - Test component interactions
   - Use test database
   - Verify data flow

3. **Functional Tests**
   - Test complete features
   - Simulate user interactions
   - End-to-end scenarios

### Example Tests

#### Authentication Test
```python
def test_login_success(client, db_session):
    """Test successful login"""
    # Create test user
    user = User(
        username='testuser',
        email='test@example.com',
        password=generate_password_hash('testpass')
    )
    db_session.add(user)
    db_session.commit()

    # Attempt login
    response = client.post('/login', data={
        'username': 'testuser',
        'password': 'testpass',
        'csrf_token': get_csrf_token(client)
    })

    assert response.status_code == 302  # Redirect after login
    assert 'Logged in successfully' in get_flashed_messages()
```

#### Book Management Test
```python
def test_add_book(client, db_session, auth):
    """Test adding a book to library"""
    auth.login()  # Login helper
    
    response = client.post('/books/add', json={
        'title': 'Test Book',
        'authors': 'Test Author',
        'status': 'to_read',
        'csrf_token': get_csrf_token(client)
    })

    assert response.status_code == 200
    assert Book.query.count() == 1
```

### Testing Security Features

#### Rate Limiting
```python
def test_rate_limit_login(client, db_session):
    """Test login rate limiting"""
    for i in range(6):  # Exceed 5 per minute limit
        response = client.post('/login', data={
            'username': 'test',
            'password': 'wrong',
            'csrf_token': get_csrf_token(client)
        })
        
        if i < 5:
            assert response.status_code == 400
        else:
            assert response.status_code == 429
```

#### CSRF Protection
```python
def test_csrf_protection(client, auth):
    """Test CSRF protection"""
    auth.login()
    
    # Attempt action without CSRF token
    response = client.post('/books/add', json={
        'title': 'Test Book'
    })
    
    assert response.status_code == 400
```

## Test Helpers

### Authentication Helper
```python
class AuthActions:
    def __init__(self, client):
        self._client = client

    def login(self, username='test', password='test'):
        return self._client.post('/login', data={
            'username': username,
            'password': password,
            'csrf_token': get_csrf_token(self._client)
        })

    def logout(self):
        return self._client.get('/logout')

@pytest.fixture
def auth(client):
    return AuthActions(client)
```

### CSRF Token Helper
```python
def get_csrf_token(client):
    """Get CSRF token from login page"""
    response = client.get('/login')
    return response.data.decode().split(
        'name="csrf_token" value="'
    )[1].split('"')[0]
```

## Best Practices

1. **Test Isolation**
   - Each test should be independent
   - Clean up after each test
   - Don't rely on test order

2. **Database Safety**
   - Always use in-memory database
   - Verify database URI in tests
   - Clean up test data

3. **Security Testing**
   - Test rate limiting
   - Verify CSRF protection
   - Check authentication requirements

4. **Test Coverage**
   - Aim for high coverage
   - Test edge cases
   - Include error scenarios

## Common Issues

1. **Database Conflicts**
   - Use unique test data
   - Clean up between tests
   - Verify cascade deletes

2. **Authentication Issues**
   - Check session handling
   - Verify CSRF tokens
   - Test login flows

3. **Rate Limiting**
   - Reset limits between tests
   - Account for timing
   - Test limit boundaries

## Continuous Integration

The test suite runs automatically on:
1. Pull requests
2. Main branch commits
3. Release tags

CI configuration ensures:
- All tests pass
- Code coverage meets threshold
- Linting passes
- Security checks complete

## Further Reading

- [pytest Documentation](https://docs.pytest.org/)
- [Flask Testing](https://flask.palletsprojects.com/en/2.0.x/testing/)
- [SQLAlchemy Testing](https://docs.sqlalchemy.org/en/14/orm/session_transaction.html)
- [Coverage.py](https://coverage.readthedocs.io/) 