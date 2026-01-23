"""
Test script for Admin Dashboard

This script generates a JWT token for an admin user and opens the dashboard
in a PyQt6 window for testing purposes.

Usage:
    python test_dashboard_admin.py
"""

import jwt
import uuid
import sys
import socket
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

# Admin user credentials (for testing)
ADMIN_USER_ID = 1
ADMIN_USERNAME = "test_admin"
ADMIN_ROLE = "admin"
ADMIN_ID = "admin_001"  # Optional: admin ID if user belongs to an admin


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
    return url, token, device_id


def check_server_accessible(base_url):
    """
    Check if the server is accessible before trying to load the page.
    
    Args:
        base_url: Base URL of the server (e.g., http://localhost:8080)
    
    Returns:
        bool: True if server is accessible, False otherwise
    """
    try:
        # Parse URL
        from urllib.parse import urlparse
        parsed = urlparse(base_url)
        host = parsed.hostname or 'localhost'
        port = parsed.port or (443 if parsed.scheme == 'https' else 80)
        
        # Try to connect to the port
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)  # 2 second timeout
        result = sock.connect_ex((host if host != 'localhost' else '127.0.0.1', port))
        sock.close()
        
        return result == 0
    except Exception as e:
        print(f"   Error checking server: {e}")
        return False


def open_dashboard_window(url, title="Dashboard"):
    """
    Open the dashboard in a PyQt6 QWebEngineView window.
    
    Args:
        url: Dashboard URL with authentication parameters
        title: Window title
    """
    from PyQt6.QtWebEngineCore import QWebEngineSettings, QWebEngineProfile
    from PyQt6.QtNetwork import QNetworkAccessManager
    
    app = QApplication(sys.argv)
    
    # Create web engine profile with proper settings
    profile = QWebEngineProfile.defaultProfile()
    
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
    
    # Try 127.0.0.1 if localhost fails (some systems have localhost resolution issues)
    if "localhost" in url:
        alt_url = url.replace("localhost", "127.0.0.1")
        print(f"Alternative URL (if localhost fails): {alt_url}")
    
    # Set URL
    qurl = QUrl(url)
    if not qurl.isValid():
        print(f"Error: Invalid URL: {url}")
        # Try alternative URL
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
    web_view.resize(1280, 720)  # Set initial window size
    
    # Track if we've tried the alternative URL
    tried_alternative = False
    
    # Add comprehensive error handling
    def handle_load_finished(ok):
        nonlocal tried_alternative
        if not ok:
            current_url = web_view.url().toString()
            print(f"❌ Failed to load page: {current_url}")
            print()
            print("   Troubleshooting steps:")
            print("   1. Verify server is running:")
            print(f"      cd react-dashboard && npm run dev")
            print("   2. Test URL in regular browser:")
            print(f"      {current_url}")
            print("   3. Check server is accessible:")
            print(f"      curl {DASHBOARD_BASE_URL}")
            print()
            
            # Try alternative URL only once
            if "localhost" in current_url and not tried_alternative:
                print("   Trying alternative URL with 127.0.0.1...")
                tried_alternative = True
                alt_url = current_url.replace("localhost", "127.0.0.1")
                web_view.setUrl(QUrl(alt_url))
            else:
                print("   💡 Tip: Copy the URL above and paste it into a regular browser")
                print("      to verify the server is working correctly.")
        else:
            print("✅ Page loaded successfully!")
            print(f"   URL: {web_view.url().toString()}")
    
    def handle_load_started():
        print("⏳ Page load started...")
    
    def handle_load_progress(progress):
        if progress % 25 == 0:  # Print every 25%
            print(f"   Loading: {progress}%")
    
    def handle_url_changed(new_url):
        print(f"📍 URL changed to: {new_url.toString()}")
    
    # Connect signals
    web_view.loadFinished.connect(handle_load_finished)
    web_view.loadStarted.connect(handle_load_started)
    web_view.loadProgress.connect(handle_load_progress)
    web_view.urlChanged.connect(handle_url_changed)
    
    web_view.show()
    
    print()
    print("=" * 60)
    print("Dashboard window opened!")
    print("If you see connection errors, check:")
    print(f"  1. Server is running: cd react-dashboard && npm run dev")
    print(f"  2. Server is accessible at: {DASHBOARD_BASE_URL}")
    print("  3. Try the URL in a regular browser first")
    print("=" * 60)
    print()
    
    # Run the application
    sys.exit(app.exec())


def main():
    """Main function to test admin dashboard."""
    print("=" * 60)
    print("Admin Dashboard Test Script")
    print("=" * 60)
    print()
    
    print(f"Dashboard URL: {DASHBOARD_BASE_URL}")
    print(f"User ID: {ADMIN_USER_ID}")
    print(f"Username: {ADMIN_USERNAME}")
    print(f"Role: {ADMIN_ROLE}")
    print()
    
    # Generate dashboard URL
    try:
        url, token, device_id = construct_dashboard_url(
            dashboard_type='admin',
            user_id=ADMIN_USER_ID,
            username=ADMIN_USERNAME,
            role=ADMIN_ROLE,
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
            
            # Check if server is accessible before opening window
            print("Checking server connectivity...")
            server_accessible = check_server_accessible(DASHBOARD_BASE_URL)
            
            if not server_accessible:
                print()
                print("⚠️  WARNING: Server does not appear to be accessible!")
                print(f"   URL: {DASHBOARD_BASE_URL}")
                print()
                print("   Please ensure:")
                print("   1. Dashboard server is running: cd react-dashboard && npm run dev")
                print("   2. Server is listening on the correct port")
                print("   3. No firewall is blocking the connection")
                print()
                response = input("Continue anyway? (y/n): ").strip().lower()
                if response != 'y' and response != 'yes':
                    print("Aborted.")
                    return 0
            
            print("Opening dashboard in PyQt window...")
            print()
            open_dashboard_window(url, "Admin Dashboard")
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
