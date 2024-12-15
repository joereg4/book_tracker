"""Test utilities and helper functions"""

def get_csrf_token(response):
    """Extract CSRF token from response"""
    return response.data.decode().split('name="csrf_token" value="')[1].split('"')[0]

def login_user(client, username, password):
    """Helper function to login a user"""
    # Get CSRF token
    response = client.get('/login')
    csrf_token = get_csrf_token(response)
    
    # Login
    return client.post('/login', data={
        'username': username,
        'password': password,
        'csrf_token': csrf_token
    }, follow_redirects=True) 