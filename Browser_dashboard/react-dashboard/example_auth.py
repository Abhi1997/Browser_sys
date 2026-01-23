"""
Example: How to pass authentication data to the dashboard

This shows how your PyQt6/QWebEngineView app should construct the dashboard URL
with the required token and deviceId parameters.
"""

import jwt
from datetime import datetime, timedelta
import uuid
from urllib.parse import urlencode

# Configuration
# For production, use: https://api.abhinavpaudel.com
# For local development, use: http://localhost:8080
DASHBOARD_BASE_URL = "https://api.abhinavpaudel.com"
SECRET_KEY = "your-secret-key-here"  # Must match your backend's secret key (from .env JWT_SECRET)

def generate_jwt_token(user_id, username, role, admin_id=None, expires_hours=24):
    """
    Generate a JWT token with user information.
    
    Args:
        user_id: User ID (int or str)
        username: Username (str)
        role: User role - 'super-admin', 'admin', 'teacher', or 'student'
        admin_id: Optional admin ID if user belongs to an admin
        expires_hours: Token expiration in hours (default: 24)
    
    Returns:
        JWT token string
    """
    now = datetime.now()
    payload = {
        'userId': user_id,  # Can also use 'user_id' (snake_case)
        'username': username,
        'role': role,
        'adminId': admin_id,
        'iat': int(now.timestamp()),  # Issued at
        'exp': int((now + timedelta(hours=expires_hours)).timestamp())  # Expiration
    }
    
    # Encode the token (use your actual secret key in production)
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token

def get_or_create_device_id():
    """
    Get existing device ID from storage or create a new one.
    In a real app, you'd store this persistently (e.g., in config file, registry, etc.)
    """
    # For this example, we'll generate a new UUID each time
    # In production, you should store and reuse the same device ID
    return str(uuid.uuid4())

def construct_dashboard_url(dashboard_type='admin', user_id=None, username=None, role=None, admin_id=None):
    """
    Construct the dashboard URL with authentication parameters.
    
    Args:
        dashboard_type: 'superadmin', 'admin', or 'teacher'
        user_id: User ID
        username: Username
        role: User role
        admin_id: Optional admin ID
    
    Returns:
        Complete dashboard URL with authentication parameters
    """
    # Generate token
    token = generate_jwt_token(user_id, username, role, admin_id)
    
    # Get or create device ID
    device_id = get_or_create_device_id()
    
    # Construct URL
    base_url = f"{DASHBOARD_BASE_URL}/dashboard-{dashboard_type}"
    params = {
        'token': token,
        'deviceId': device_id
    }
    
    url = f"{base_url}?{urlencode(params)}"
    return url

# Example usage
if __name__ == "__main__":
    # Example 1: Admin user
    admin_url = construct_dashboard_url(
        dashboard_type='admin',
        user_id=123,
        username='john_doe',
        role='admin',
        admin_id='admin_001'
    )
    print("Admin Dashboard URL:")
    print(admin_url)
    print()
    
    # Example 2: Super Admin user
    superadmin_url = construct_dashboard_url(
        dashboard_type='superadmin',
        user_id=1,
        username='super_admin',
        role='super-admin'
    )
    print("Super Admin Dashboard URL:")
    print(superadmin_url)
    print()
    
    # Example 3: Teacher user
    teacher_url = construct_dashboard_url(
        dashboard_type='teacher',
        user_id=456,
        username='jane_smith',
        role='teacher',
        admin_id='admin_001'
    )
    print("Teacher Dashboard URL:")
    print(teacher_url)
    print()
    
    # In PyQt6, you would use it like this:
    # from PyQt6.QtCore import QUrl
    # web_view.setUrl(QUrl(admin_url))
