# API Documentation

## Overview

The Book Tracker API provides programmatic access to book management functionality. The API follows REST principles and uses JSON for request and response bodies.

## Base URL

All API URLs are relative to:
```
http://your-domain.com/
```

For local development:
```
http://127.0.0.1:5000/
```

## Authentication

Most endpoints require authentication. The application uses session-based authentication with CSRF protection.

See [Authentication](authentication.md) for details.

## Rate Limiting

To protect the service from abuse, rate limiting is implemented on certain endpoints:

- Login attempts: 5 per minute
- Book searches: 30 per minute

See [Rate Limiting](rate-limiting.md) for details.

## Common Endpoints

### Authentication

- `POST /login` - User login
- `POST /signup` - User registration
- `POST /logout` - User logout
- `POST /forgot-password` - Request password reset
- `POST /reset-password/<token>` - Reset password with token
- `GET /oauth2callback` - OAuth2 callback handler
- `GET /authorize` - Initiate OAuth2 flow

### Books

- `GET /books/search` - Search Google Books API
- `POST /books/add` - Add book to library
- `GET /books/<id>` - Get book details
- `POST /books/<id>/update` - Update book status
- `DELETE /books/<id>` - Remove book from library

### Shelves

- `GET /shelf` - View all shelves
- `GET /shelf/search` - Search within library
- `GET /shelf/<status>` - View specific shelf

### Profile

- `GET /profile` - View user profile
- `POST /profile/update` - Update profile
- `POST /profile/delete` - Delete account
- `GET /profile/export/csv` - Export library as CSV
- `GET /profile/export/json` - Export library as JSON

### Statistics

- `GET /stats` - View reading statistics
- `GET /stats/categories` - View category statistics

## Response Format

Successful responses follow this format:
```json
{
    "status": "success",
    "data": {
        // Response data here
    }
}
```

Error responses follow this format:
```json
{
    "status": "error",
    "message": "Error description",
    "code": "ERROR_CODE"
}
```

## Common Status Codes

- `200 OK` - Request succeeded
- `201 Created` - Resource created
- `400 Bad Request` - Invalid request
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Server error

## CSRF Protection

All POST, PUT, DELETE requests require a CSRF token. The token should be:
1. Obtained from the `csrf_token()` template function
2. Included in form data or headers as `csrf_token`

## Error Handling

The API uses standard HTTP status codes and includes detailed error messages in the response body.

Example error response:
```json
{
    "status": "error",
    "message": "Rate limit exceeded",
    "code": "RATE_LIMIT_EXCEEDED",
    "retry_after": 30
}
```

## Further Documentation

- [Authentication Details](authentication.md)
- [Endpoint Reference](endpoints.md)
- [Rate Limiting Details](rate-limiting.md)

## Support

For API support:
1. Check the [FAQ](../faq.md)
2. Search [existing issues](https://github.com/joereg4/book_tracker/issues)
3. Create a new issue if needed 