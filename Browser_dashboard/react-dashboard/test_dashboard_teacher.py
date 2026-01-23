"""
Test script for Teacher Dashboard

This script generates a JWT token for a teacher user and opens the dashboard
in a PyQt6 window for testing purposes.

Usage:
    python test_dashboard_teacher.py
"""

import jwt
import uuid
import sys
from datetime import datetime, timedelta
from urllib.parse import urlencode

try:
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import QUrl
    from PyQt6.QtWebEngineWidgets import QWebEngineView
    PYQT6_AVAILABLE = True
except ImportError:
    PYQT6_AVAILABLE = False
    print("Warning: PyQt6 not available. Install with: pip install PyQt6")

# Configuration
DASHBOARD_BASE_URL = "http://localhost:3000"  # Change to https://api.abhinavpaudel.com for production
# Note: If your dashboard runs on a different port, update this URL
JWT_SECRET = "your-super-secret-jwt-key-change-this-in-production"  # Must match your backend's JWT_SECRET

# Teacher user credentials (for testing)
TEACHER_USER_ID = 2
TEACHER_USERNAME = "test_teacher"
TEACHER_ROLE = "teacher"
ADMIN_ID = "admin_001"  # Teacher belongs to an admin


def generate_jwt_token(user_id, username, role, admin_id=None, expires_hours=24):
    """
    Generate a JWT token with user information.
    
    Args:
        user_id: User ID (int)
        username: Username (str)
        role: User role (str) - 'admin', 'super-admin', 'teacher', or 'student'
        admin_id: Optional admin ID (str)
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
    
    # Encode the token
    token = jwt.encode(payload, JWT_SECRET, algorithm='HS256')
    return token


def get_or_create_device_id():
    """
    Get existing device ID or create a new one.
    For testing, we'll generate a new UUID each time.
    In production, you'd store this persistently.
    """
    return str(uuid.uuid4())


def construct_dashboard_url(dashboard_type='teacher', user_id=None, username=None, role=None, admin_id=None):
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
    return url, token, device_id


def open_dashboard_window(url, title="Dashboard"):
    """
    Open the dashboard in a PyQt6 QWebEngineView window.
    
    Args:
        url: Dashboard URL with authentication parameters
        title: Window title
    """
    from PyQt6.QtWebEngineCore import QWebEngineSettings, QWebEngineProfile
    
    app = QApplication(sys.argv)
    
    # Create web engine view
    web_view = QWebEngineView()
    web_view.setWindowTitle(title)
    
    # Enable local content and fix localhost connection issues
    settings = web_view.settings()
    settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
    settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
    settings.setAttribute(QWebEngineSettings.WebAttribute.AllowRunningInsecureContent, True)
    settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
    settings.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)
    
    # Print URL for debugging
    print(f"Loading URL: {url}")
    
    # Try 127.0.0.1 if localhost fails
    if "localhost" in url:
        alt_url = url.replace("localhost", "127.0.0.1")
        print(f"Alternative URL (if localhost fails): {alt_url}")
    
    # Set URL
    qurl = QUrl(url)
    if not qurl.isValid():
        print(f"Error: Invalid URL: {url}")
        if "localhost" in url:
            qurl = QUrl(alt_url)
            if qurl.isValid():
                print(f"Using alternative URL: {alt_url}")
                url = alt_url
            else:
                return
        else:
            return
    
    web_view.setUrl(qurl)
    web_view.resize(1280, 720)
    
    # Add comprehensive error handling
    def handle_load_finished(ok):
        if not ok:
            current_url = web_view.url().toString()
            print(f"❌ Failed to load page: {current_url}")
            if "localhost" in current_url:
                alt_url = current_url.replace("localhost", "127.0.0.1")
                web_view.setUrl(QUrl(alt_url))
        else:
            print("✅ Page loaded successfully!")
    
    def handle_load_started():
        print("⏳ Page load started...")
    
    web_view.loadFinished.connect(handle_load_finished)
    web_view.loadStarted.connect(handle_load_started)
    
    web_view.show()
    sys.exit(app.exec())


def main():
    """Main function to test teacher dashboard."""
    print("=" * 60)
    print("Teacher Dashboard Test Script")
    print("=" * 60)
    print()
    
    print(f"Dashboard URL: {DASHBOARD_BASE_URL}")
    print(f"User ID: {TEACHER_USER_ID}")
    print(f"Username: {TEACHER_USERNAME}")
    print(f"Role: {TEACHER_ROLE}")
    print(f"Admin ID: {ADMIN_ID}")
    print()
    
    # Generate dashboard URL
    try:
        url, token, device_id = construct_dashboard_url(
            dashboard_type='teacher',
            user_id=TEACHER_USER_ID,
            username=TEACHER_USERNAME,
            role=TEACHER_ROLE,
            admin_id=ADMIN_ID
        )
        
        print("Generated JWT Token:")
        print(f"  {token[:50]}...")
        print()
        print("Device ID:")
        print(f"  {device_id}")
        print()
        print("Dashboard URL:")
        print(f"  {url}")
        print()
        
        # Decode token to verify (for debugging)
        try:
            decoded = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
            print("Token Payload (decoded):")
            for key, value in decoded.items():
                print(f"  {key}: {value}")
            print()
        except Exception as e:
            print(f"Warning: Could not decode token: {e}")
            print()
        
        # Ask user if they want to open in PyQt window
        response = input("Open dashboard in PyQt window? (y/n): ").strip().lower()
        if response == 'y' or response == 'yes':
            if not PYQT6_AVAILABLE:
                print("Error: PyQt6 is not installed.")
                print("Install it with: pip install PyQt6")
                print()
                print("Dashboard URL (copy and paste into browser):")
                print(url)
                return 1
            
            print("Opening dashboard in PyQt window...")
            open_dashboard_window(url, "Teacher Dashboard")
            print("Dashboard window closed.")
        else:
            print("Dashboard URL generated. Copy and paste it into your browser:")
            print(url)
        
    except Exception as e:
        print(f"Error generating dashboard URL: {e}")
        print()
        print("Troubleshooting:")
        print("1. Ensure PyJWT is installed: pip install PyJWT")
        print("2. Check JWT_SECRET matches your backend configuration")
        print("3. Verify DASHBOARD_BASE_URL is correct")
        return 1
    
    print()
    print("=" * 60)
    print("Test completed!")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    exit(main())
