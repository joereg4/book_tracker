# Security Policy

## Security Features

Book Tracker implements several security measures:

1. **Authentication & Authorization**
   - Secure password hashing
   - OAuth2 authentication for email services
   - Rate limiting on authentication endpoints
   - Session management with secure cookies

2. **Data Protection**
   - CSRF protection on all forms
   - Secure handling of environment variables
   - Database backup and restore utilities
   - Input validation and sanitization

3. **API Security**
   - Rate limiting on API endpoints
   - Secure handling of API keys
   - OAuth2 for third-party integrations

## Reporting a Vulnerability

We take the security of Book Tracker seriously. If you believe you have found a security vulnerability, please report it by creating a new Issue:

1. Go to the [Issues](https://github.com/joereg4/book-tracker/issues) section
2. Click "New Issue"
3. Use the title format: `[SECURITY] Brief description of vulnerability`
4. In the description, please include:
   - A detailed description of the vulnerability
   - Steps to reproduce the vulnerability
   - Potential impact
   - Suggested fixes (if any)

## What to Expect

- We will acknowledge your report within 48 hours
- We will provide updates as we investigate the issue
- Once resolved, we will credit you in the fix (unless you prefer to remain anonymous)

## Guidelines

- Please do not disclose the vulnerability publicly until we have had a chance to address it
- Provide sufficient information to reproduce and verify the vulnerability
- Only test against test accounts and test data
- Do not access or modify other users' data
- Do not execute denial of service attacks

Thank you for helping keep Book Tracker secure! 