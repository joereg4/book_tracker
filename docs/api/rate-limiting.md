# Rate Limiting

## Overview

Rate limiting is implemented to protect the API from abuse and ensure fair usage. Different endpoints have different rate limits based on their resource intensity and security requirements.

## Rate Limits

### Authentication Endpoints

- Login attempts: 5 per minute per IP
- Password reset requests: 3 per hour per IP
- Account creation: 3 per hour per IP

### Book Management

- Book searches: 30 per minute per user
- Book additions: 50 per hour per user
- Book updates: 100 per hour per user
- Book deletions: 50 per hour per user

### API Endpoints

- General API calls: 100 per minute per user
- OAuth2 token requests: 10 per minute per user
- Export operations: 2 per hour per user

## Response Headers

Rate limit information is included in response headers:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

- `X-RateLimit-Limit`: Maximum requests allowed in the window
- `X-RateLimit-Remaining`: Remaining requests in the current window
- `X-RateLimit-Reset`: Timestamp when the rate limit resets

## Rate Limit Exceeded

When a rate limit is exceeded, the API returns:

```json
{
    "status": "error",
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Please try again in 30 seconds.",
    "retry_after": 30
}
```

With HTTP status code `429 Too Many Requests`.

## Best Practices

1. **Implement Retries**:
   - Use exponential backoff
   - Respect the `retry_after` value
   - Handle 429 responses gracefully

2. **Monitor Usage**:
   - Track remaining requests
   - Pre-emptively slow down
   - Implement request queuing

3. **Optimize Requests**:
   - Batch operations when possible
   - Cache responses
   - Use conditional requests 