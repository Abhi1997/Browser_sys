"""
Login with admin credentials and open dashboard

This script:
1. Logs in to the backend with admin credentials
2. Gets a JWT token from the backend
3. Opens the dashboard in PyQt6 window with real authentication

Usage:
    python backend/login_and_test.py
"""

import requests
import sys
import uuid

try:
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import QUrl
    from PyQt6.QtWebEngineWidgets import QWebEngineView
    from PyQt6.QtWebEngineCore import QWebEngineSettings
    PYQT6_AVAILABLE = True
except ImportError:
    PYQT6_AVAILABLE = False
    print("Warning: PyQt6 not available. Install with: pip install PyQt6")

BACKEND_URL = "http://localhost:5000"
DASHBOARD_URL = "http://localhost:3000"

# Admin credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123!"

def login_and_get_token():
    """Login to backend and get JWT token"""
    print("=" * 60)
    print("Admin Login to Backend")
    print("=" * 60)
    print()
    
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Username: {ADMIN_USERNAME}")
    print()
    
    device_id = str(uuid.uuid4())
    
    login_data = {
        "username": ADMIN_USERNAME,
        "password": ADMIN_PASSWORD,
        "deviceId": device_id
    }
    
    try:
        print("Logging in...")
        response = requests.post(
            f"{BACKEND_URL}/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                token = data['data']['token']
                user = data['data']['user']
                
                print("✅ Login successful!")
                print()
                print("User Information:")
                print(f"  ID: {user['id']}")
                print(f"  Username: {user['username']}")
                print(f"  Role: {user['role']}")
                print(f"  Email: {user.get('email', 'N/A')}")
                print()
                
                return token, device_id, user
            else:
                print(f"❌ Login failed: {data.get('error', 'Unknown error')}")
                return None, None, None
        else:
            print(f"❌ Login failed: HTTP {response.status_code}")
            try:
                error_data = response.json()
                print(f"  Error: {error_data.get('error', 'Unknown error')}")
            except:
                print(f"  Response: {response.text}")
            return None, None, None
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend server!")
        print()
        print("Please start the backend server first:")
        print("  cd backend")
        print("  python app.py")
        return None, None, None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None, None, None

def open_dashboard(token, device_id, user):
    """Open dashboard in PyQt6 window"""
    if not PYQT6_AVAILABLE:
        print("PyQt6 not available. Dashboard URL:")
        role_path = user['role'].replace('super-admin', 'superadmin')
        url = f"{DASHBOARD_URL}/dashboard-{role_path}?token={token}&deviceId={device_id}"
        print(url)
        return
    
    from urllib.parse import urlencode
    
    role_path = user['role'].replace('super-admin', 'superadmin')
    params = {
        'token': token,
        'deviceId': device_id
    }
    url = f"{DASHBOARD_URL}/dashboard-{role_path}?{urlencode(params)}"
    
    print("Opening dashboard in PyQt6 window...")
    print(f"URL: {url}")
    print()
    
    app = QApplication(sys.argv)
    web_view = QWebEngineView()
    web_view.setWindowTitle(f"Dashboard - {user['username']} ({user['role']})")
    
    # Enable local content
    settings = web_view.settings()
    settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
    settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
    settings.setAttribute(QWebEngineSettings.WebAttribute.AllowRunningInsecureContent, True)
    settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
    settings.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)
    
    web_view.setUrl(QUrl(url))
    web_view.resize(1280, 720)
    web_view.show()
    
    sys.exit(app.exec())

def main():
    """Main function"""
    token, device_id, user = login_and_get_token()
    
    if not token:
        print()
        print("=" * 60)
        print("Login failed. Please check:")
        print("  1. Backend server is running: python backend/app.py")
        print("  2. Admin credentials are correct")
        print("  3. Database is accessible")
        print("=" * 60)
        return 1
    
    print("=" * 60)
    response = input("Open dashboard in PyQt window? (y/n): ").strip().lower()
    
    if response == 'y' or response == 'yes':
        open_dashboard(token, device_id, user)
    else:
        role_path = user['role'].replace('super-admin', 'superadmin')
        from urllib.parse import urlencode
        params = {'token': token, 'deviceId': device_id}
        url = f"{DASHBOARD_URL}/dashboard-{role_path}?{urlencode(params)}"
        print()
        print("Dashboard URL:")
        print(url)
    
    return 0

if __name__ == "__main__":
    exit(main())
