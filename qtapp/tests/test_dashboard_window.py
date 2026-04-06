"""
Test script to open the Dashboard Window directly.
Bypasses the main browser while still using the proper login flow.
Connects to the local Vite dev server (npm run dev) at localhost:8080.
Usage:
  1. cd Browser_dashboard/react-dashboard && npm run dev    (start frontend)
  2. python tests/test_dashboard_window.py                  (run this test)
"""
import sys
import os

# Point dashboard at local dev server instead of production
os.environ["DASHBOARD_URL"] = "http://localhost:8080"

# Add parent directory to path so we can import the qtapp modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt6.QtCore import QSettings

from dashboard_window import DashboardWindow
from gmail_oauth import GmailLoginWindow
from browser import apply_app_theme

# Import browser namespace to fake isinstance(parent, browser.MainWindow)
import browser

class MockBrowserWindow(QMainWindow):
    """A mock main window to act as parent for the dashboard"""
    def __init__(self, auth, user_id, username, user_role, gmail=None):
        super().__init__()
        self.auth = auth
        self.user_id = user_id
        self.username = username
        self.user_role = user_role
        self.gmail = gmail

# Trick the type checker in open_management to allow switching windows
browser.MainWindow = MockBrowserWindow

def main():
    app = QApplication(sys.argv)
    
    # Optional: Apply dark mode if set
    dark = QSettings("EduBrowser", "Settings").value("dark_mode", False, type=bool)
    apply_app_theme(dark)
    
    print("Opening Login Window to authenticate properly...")
    print(f"Dashboard URL: {os.environ['DASHBOARD_URL']}")
    login_window = GmailLoginWindow()
    login_window.exec()
    
    if getattr(login_window, "login_successful", False):
        user_role = getattr(login_window, "user_role", None)
        
        if user_role == "student":
            QMessageBox.warning(None, "Access Denied", "Students do not have access to the dashboard.")
            sys.exit(1)
            
        print(f"Logged in successfully as {user_role}. Launching DashboardWindow...")
        
        # Create a mock parent similar to what MainWindow does
        mock_parent = MockBrowserWindow(
            auth=login_window.auth,
            user_id=getattr(login_window, "user_id", None),
            username=getattr(login_window, "username", None),
            user_role=user_role,
            gmail=getattr(login_window, "gmail", None)
        )
        
        # Launch Dashboard directly
        dash = DashboardWindow(mock_parent)
        dash.show()
        sys.exit(app.exec())
    else:
        print("Login failed or cancelled.")
        sys.exit(0)

if __name__ == "__main__":
    main()
