"""
Test script to open the Management Window directly.
Bypasses the main browser while still using the proper login flow.
Run this from the qtapp directory or within tests/.
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt6.QtCore import QSettings

from management_window import ManagementWindow
from gmail_oauth import GmailLoginWindow
from browser import apply_app_theme

# Import browser namespace to fake isinstance(parent, browser.MainWindow)
import browser

class MockBrowserWindow(QMainWindow):
    """A mock main window to act as parent for the management window"""
    def __init__(self, auth, user_id, username, user_role, gmail=None):
        super().__init__()
        self.auth = auth
        self.user_id = user_id
        self.username = username
        self.user_role = user_role
        self.gmail = gmail

# Trick the type checker in back_to_dashboard to allow switching windows
browser.MainWindow = MockBrowserWindow

def main():
    app = QApplication(sys.argv)
    
    dark = QSettings("EduBrowser", "Settings").value("dark_mode", False, type=bool)
    apply_app_theme(dark)
    
    print("Opening Login Window to authenticate properly...")
    login_window = GmailLoginWindow()
    login_window.exec()
    
    if getattr(login_window, "login_successful", False):
        user_role = getattr(login_window, "user_role", None)
        
        if user_role not in ["admin", "superadmin", "superuser", "super-admin"]:
            QMessageBox.warning(None, "Access Denied", f"Management Window requires admin/superadmin role. Your role is: {user_role}")
            sys.exit(1)
            
        print(f"Logged in successfully as {user_role}. Launching ManagementWindow...")
        
        # Create a mock parent similar to what MainWindow does
        mock_parent = MockBrowserWindow(
            auth=login_window.auth,
            user_id=getattr(login_window, "user_id", None),
            username=getattr(login_window, "username", None),
            user_role=user_role,
            gmail=getattr(login_window, "gmail", None)
        )
        
        # Launch Management Window bypass
        mgmt = ManagementWindow(mock_parent)
        mgmt.show()
        sys.exit(app.exec())
    else:
        print("Login failed or cancelled.")
        sys.exit(0)

if __name__ == "__main__":
    main()
