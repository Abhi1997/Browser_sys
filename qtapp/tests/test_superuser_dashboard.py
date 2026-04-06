"""
Automated Test execution for SUPERUSER dashboard
Connects to the local Vite dev server (npm run dev) at localhost:8080.
Usage:
  1. cd Browser_dashboard/react-dashboard && npm run dev    (start frontend)
  2. python tests/test_superuser_dashboard.py               (run this test)
"""
import sys
import os

# Point dashboard at local dev server instead of production
os.environ["DASHBOARD_URL"] = "http://localhost:8080"

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox
from authentication import Authentication
from dashboard_window import DashboardWindow
import browser

# Mock main window to skip browser startup
class MockBrowserWindow(QMainWindow):
    def __init__(self, auth, user_id, username, user_role, gmail=None):
        super().__init__()
        self.auth = auth
        self.user_id = user_id
        self.username = username
        self.user_role = user_role
        self.gmail = gmail

browser.MainWindow = MockBrowserWindow

def main():
    app = QApplication(sys.argv)
    
    auth = Authentication()
    device_id = auth.get_device_info().get('device_id')
    
    username = "admin"
    password = "admin123!"
    
    print(f"Logging in automatically as {username}...")
    print(f"Dashboard URL: {os.environ['DASHBOARD_URL']}")
    
    result = auth.authenticate_user(username, password, device_id)
    if not result or not result.get("success"):
        error = result.get("error", "Unknown error") if result else "Connection failed"
        QMessageBox.critical(None, "Login Failed", f"Failed to login {username}: {error}")
        sys.exit(1)
        
    user_info = result.get("user", {})
    user_role = user_info.get("role")
    
    if user_role == "student":
        QMessageBox.warning(None, "Access Denied", "Students do not have access to the dashboard.")
        sys.exit(1)
        
    print(f"Success! Launching DashboardWindow for role: {user_role}")
    
    mock_parent = MockBrowserWindow(
        auth=auth,
        user_id=user_info.get("id"),
        username=user_info.get("username"),
        user_role=user_role,
        gmail=user_info.get("gmail")
    )
    
    # Launch Dashboard
    dash = DashboardWindow(mock_parent)
    dash.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
