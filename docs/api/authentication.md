# Authentication

## Overview

Book Tracker uses two types of authentication:
1. Session-based authentication for user access
2. OAuth2 authentication for email services

## Session-based Authentication

### Login

**Endpoint**: `POST /login`

Request body:
```json
{
    "username": "user@example.com",
    "password": "secure_password",
    "remember_me": true
}
```

Response:
```json
{
    "status": "success",
    "data": {
        "user_id": 123,
        "username": "username"
    }
}
```

### Registration

**Endpoint**: `POST /signup`

Request body:
```json
{
    "username": "newuser",
    "email": "user@example.com",
    "password": "secure_password"
}
```

### Password Reset

1. Request reset: `POST /forgot-password`
2. Reset password: `POST /reset-password/<token>`

## OAuth2 Authentication

### Gmail OAuth2

Used for sending emails through Gmail's SMTP server.

1. **Authorization Flow**:
   - Redirect to Google's consent screen
   - User grants permissions
   - Receive authorization code
   - Exchange for access/refresh tokens

2. **Endpoints**:
   - `GET /authorize` - Start OAuth2 flow
   - `GET /oauth2callback` - Handle OAuth2 callback

3. **Token Management**:
   - Tokens stored securely in database
   - Automatic token refresh
   - Secure token rotation

### Security Considerations

1. **Session Security**:
   - CSRF protection on all forms
   - Secure session cookies
   - Session timeout
   - Rate limiting

2. **Password Security**:
   - Bcrypt password hashing
   - Password complexity requirements
   - Brute force protection

3. **OAuth2 Security**:
   - Secure token storage
   - HTTPS for all OAuth2 traffic
   - State parameter validation
   - Prompt consent for sensitive scopes 