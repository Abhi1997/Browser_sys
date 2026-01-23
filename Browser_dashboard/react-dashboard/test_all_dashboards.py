"""
Test script for All Dashboards

This script generates JWT tokens for admin, super admin, and teacher users
and opens all dashboards in PyQt6 windows for testing purposes.

Usage:
    python test_all_dashboards.py
"""

import jwt
import uuid
import sys
from datetime import datetime, timedelta
from urllib.parse import urlencode

try:
    from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget
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


def generate_jwt_token(user_id, username, role, admin_id=None, expires_hours=24):
    """Generate a JWT token with user information."""
    now = datetime.now()
    payload = {
        'userId': user_id,
        'username': username,
        'role': role,
        'adminId': admin_id,
        'iat': int(now.timestamp()),
        'exp': int((now + timedelta(hours=expires_hours)).timestamp())
    }
    return jwt.encode(payload, JWT_SECRET, algorithm='HS256')


def get_device_id():
    """Generate a device ID."""
    return str(uuid.uuid4())


def construct_dashboard_url(dashboard_type, user_id, username, role, admin_id=None):
    """Construct the dashboard URL with authentication parameters."""
    token = generate_jwt_token(user_id, username, role, admin_id)
    device_id = get_device_id()
    base_url = f"{DASHBOARD_BASE_URL}/dashboard-{dashboard_type}"
    params = {'token': token, 'deviceId': device_id}
    url = f"{base_url}?{urlencode(params)}"
    return url, token, device_id


def open_all_dashboards(urls):
    """
    Open all dashboards in separate PyQt6 windows or tabs.
    
    Args:
        urls: List of dictionaries with 'type', 'url', and 'username' keys
    """
    from PyQt6.QtWebEngineCore import QWebEngineSettings
    
    app = QApplication(sys.argv)
    
    # Option 1: Open in separate windows
    windows = []
    for dashboard in urls:
        web_view = QWebEngineView()
        title = f"{dashboard['type'].upper()} Dashboard - {dashboard['username']}"
        web_view.setWindowTitle(title)
        
        # Enable local content and fix localhost connection issues
        settings = web_view.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.AllowRunningInsecureContent, True)
        
        # Print URL for debugging
        print(f"Loading {dashboard['type']} dashboard: {dashboard['url']}")
        
        # Set URL
        qurl = QUrl(dashboard['url'])
        if not qurl.isValid():
            print(f"Error: Invalid URL: {dashboard['url']}")
            continue
        
        web_view.setUrl(qurl)
        web_view.resize(1280, 720)
        
        # Add error handling
        def handle_load_finished(ok, view=web_view, dash_type=dashboard['type']):
            if not ok:
                print(f"Failed to load {dash_type} dashboard. Status: {view.url().toString()}")
                view.reload()
        
        web_view.loadFinished.connect(handle_load_finished)
        web_view.show()
        windows.append(web_view)
    
    # Option 2: Open in tabs (uncomment to use tabs instead)
    # main_window = QMainWindow()
    # main_window.setWindowTitle("Dashboard Tester")
    # main_window.resize(1280, 720)
    # 
    # tab_widget = QTabWidget()
    # main_window.setCentralWidget(tab_widget)
    # 
    # for dashboard in urls:
    #     web_view = QWebEngineView()
    #     web_view.setUrl(QUrl(dashboard['url']))
    #     tab_name = f"{dashboard['type'].upper()} - {dashboard['username']}"
    #     tab_widget.addTab(web_view, tab_name)
    # 
    # main_window.show()
    
    # Run the application
    sys.exit(app.exec())


def main():
    """Main function to test all dashboards."""
    print("=" * 60)
    print("All Dashboards Test Script")
    print("=" * 60)
    print()
    
    # Test users
    test_users = [
        {
            'type': 'superadmin',
            'user_id': 1,
            'username': 'test_superadmin',
            'role': 'super-admin',
            'admin_id': None
        },
        {
            'type': 'admin',
            'user_id': 2,
            'username': 'test_admin',
            'role': 'admin',
            'admin_id': 'admin_001'
        },
        {
            'type': 'teacher',
            'user_id': 3,
            'username': 'test_teacher',
            'role': 'teacher',
            'admin_id': 'admin_001'
        }
    ]
    
    urls = []
    
    print("Generating dashboard URLs...")
    print()
    
    for user in test_users:
        try:
            url, token, device_id = construct_dashboard_url(
                dashboard_type=user['type'],
                user_id=user['user_id'],
                username=user['username'],
                role=user['role'],
                admin_id=user['admin_id']
            )
            
            urls.append({
                'type': user['type'],
                'url': url,
                'username': user['username']
            })
            
            print(f"{user['type'].upper()} Dashboard:")
            print(f"  User: {user['username']}")
            print(f"  Role: {user['role']}")
            print(f"  URL: {url}")
            print()
            
        except Exception as e:
            print(f"Error generating {user['type']} dashboard URL: {e}")
            print()
    
    if not urls:
        print("No URLs generated. Check your configuration.")
        return 1
    
    # Ask user if they want to open in PyQt windows
    print("=" * 60)
    response = input("Open all dashboards in PyQt windows? (y/n): ").strip().lower()
    
    if response == 'y' or response == 'yes':
        if not PYQT6_AVAILABLE:
            print("Error: PyQt6 is not installed.")
            print("Install it with: pip install PyQt6")
            print()
            print("Dashboard URLs (copy and paste into browser):")
            print()
            for dashboard in urls:
                print(f"{dashboard['type'].upper()} ({dashboard['username']}):")
                print(f"  {dashboard['url']}")
                print()
            return 1
        
        print()
        print("Opening dashboards in PyQt windows...")
        open_all_dashboards(urls)
        print("All dashboard windows closed.")
    else:
        print()
        print("Dashboard URLs generated. Copy and paste them into your browser:")
        print()
        for dashboard in urls:
            print(f"{dashboard['type'].upper()} ({dashboard['username']}):")
            print(f"  {dashboard['url']}")
            print()
    
    print()
    print("=" * 60)
    print("Test completed!")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    exit(main())
