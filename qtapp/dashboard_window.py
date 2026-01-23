"""
Dashboard Window Module
Opens the web dashboard at api.abhinavpaudel.com with authentication
"""

from PyQt6.QtCore import QUrl
from PyQt6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QApplication, QStyle, QMessageBox
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
import urllib.parse
import os


class DashboardWindow(QDialog):
    """Dashboard window for admin and teacher roles"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("EduBrowser Dashboard")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)
        
        # Get user info from parent
        self.auth = None
        self.user_id = None
        self.username = None
        self.user_role = None
        
        if parent and hasattr(parent, 'auth'):
            self.auth = parent.auth
            self.user_id = getattr(parent, 'user_id', None)
            self.username = getattr(parent, 'username', None)
            self.user_role = getattr(parent, 'user_role', None)
        
        # Validate we have required info
        if not all([self.auth, self.user_id, self.username, self.user_role]):
            QMessageBox.critical(
                self,
                "Authentication Error",
                "Missing required user information. Please log in again."
            )
            self.reject()
            return
        
        # Create layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Add Management button at the top (highly visible)
        button_container = QWidget()
        button_container.setStyleSheet("background-color: #1f2937; padding: 8px;")
        button_container.setFixedHeight(50)
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(10, 5, 10, 5)
        button_layout.setSpacing(10)
        
        management_btn = QPushButton("Management Panel")
        management_btn.setToolTip("Open User & Site Management")
        management_btn.setFixedHeight(35)
        management_btn.setMinimumWidth(150)
        management_btn.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border: 2px solid #2563eb;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
                padding: 5px 15px;
            }
            QPushButton:hover {
                background-color: #2563eb;
                border-color: #1d4ed8;
            }
            QPushButton:pressed {
                background-color: #1d4ed8;
            }
        """)
        management_btn.clicked.connect(self.open_management)
        button_layout.addWidget(management_btn)
        button_layout.addStretch()
        layout.addWidget(button_container)
        
        # Create web view for dashboard
        self.view = QWebEngineView(self)
        layout.addWidget(self.view)
        
        # Load dashboard URL with authentication
        dashboard_url = self._build_dashboard_url()
        if dashboard_url:
            self.view.setUrl(QUrl(dashboard_url))
        else:
            QMessageBox.critical(
                self,
                "Error",
                "Failed to generate dashboard URL. Please try again."
            )
            self.reject()
            return
        
        # Set window icon
        self.setWindowIcon(QApplication.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon))
    
    def _generate_dashboard_token(self):
        """Generate JWT token for dashboard authentication"""
        try:
            # Use the authentication module's generate_token method
            # It already handles userId/user_id, username, role, exp, iat
            token = self.auth.generate_token(
                username=self.username,
                role=self.user_role,
                user_id=self.user_id
            )
            
            # jwt.encode returns string in PyJWT >= 2.0, bytes in older versions
            if isinstance(token, bytes):
                token = token.decode('utf-8')
            
            return token
        except Exception as e:
            print(f"Error generating dashboard token: {e}")
            return None
    
    def _get_device_id(self):
        """Get or generate device ID"""
        try:
            # Try to get device info from auth
            device_info = self.auth.get_device_info()
            device_id = device_info.get("device_id")
            
            if device_id:
                return device_id
            
            # If no device_id, generate one
            import uuid
            device_id = str(uuid.uuid4())
            return device_id
        except Exception as e:
            print(f"Error getting device ID: {e}")
            # Fallback: generate a device ID
            import uuid
            return str(uuid.uuid4())
    
    def _build_dashboard_url(self):
        """Build dashboard URL with authentication parameters"""
        try:
            # Generate token
            token = self._generate_dashboard_token()
            if not token:
                return None
            
            # Get device ID
            device_id = self._get_device_id()
            
            # Map role to dashboard path
            role_paths = {
                "superadmin": "dashboard-superadmin",
                "admin": "dashboard-admin",
                "teacher": "dashboard-teacher"
            }
            
            dashboard_path = role_paths.get(self.user_role.lower(), "dashboard-admin")
            
            # Base URL - use environment variable or default
            base_url = os.getenv("DASHBOARD_URL", "https://api.abhinavpaudel.com")
            
            # Remove trailing slash if present
            base_url = base_url.rstrip('/')
            
            # Construct full URL with query parameters
            dashboard_url = f"{base_url}/{dashboard_path}?token={urllib.parse.quote(token)}&deviceId={urllib.parse.quote(device_id)}"
            
            return dashboard_url
        except Exception as e:
            print(f"Error building dashboard URL: {e}")
            return None
    
    def open_management(self):
        """Open management window and close dashboard"""
        from management_window import ManagementWindow
        parent = self.parent()
        if parent:
            # Import MainWindow to check type
            from browser import MainWindow
            if isinstance(parent, MainWindow):
                management_window = ManagementWindow(parent)
                management_window.show()
                self.close()  # Close dashboard window
