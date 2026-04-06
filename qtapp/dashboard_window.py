"""
Dashboard Window Module
Opens the web dashboard at api.abhinavpaudel.com with authentication
"""

from datetime import datetime
import urllib.parse
import os

from PyQt6.QtCore import QUrl
from PyQt6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QApplication, QStyle, QMessageBox,
    QPlainTextEdit, QDialogButtonBox, QTabWidget,
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage


class _DashboardWebPage(QWebEnginePage):
    """Custom page that captures JS console messages (log, warn, error) via override."""
    def __init__(self, profile, on_console_message):
        super().__init__(profile)
        self._on_console = on_console_message

    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):
        if callable(self._on_console):
            try:
                self._on_console(level, message, lineNumber, sourceID)
            except Exception:
                pass


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
        
        # Add Management button at the top for admin/superadmin/superuser (not for teachers)
        role_lower = (self.user_role or "").lower()
        show_management = role_lower in ("admin", "superadmin", "super-admin", "superuser")
        button_container = QWidget()
        button_container.setStyleSheet("background-color: #1f2937; padding: 8px;")
        button_container.setFixedHeight(50)
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(10, 5, 10, 5)
        button_layout.setSpacing(10)
        if show_management:
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
        # Debug log button (all roles) - view API/dashboard console messages
        self._console_log = []
        self._console_log_max = 300
        debug_btn = QPushButton("Debug log")
        debug_btn.setToolTip("View dashboard console messages and API errors")
        debug_btn.setFixedHeight(35)
        debug_btn.setMinimumWidth(100)
        debug_btn.setStyleSheet("""
            QPushButton {
                background-color: #4b5563;
                color: white;
                border: 1px solid #374151;
                border-radius: 5px;
                font-size: 12px;
                padding: 5px 10px;
            }
            QPushButton:hover { background-color: #374151; }
        """)
        debug_btn.clicked.connect(self._show_debug_log)
        button_layout.addWidget(debug_btn)
        button_layout.addStretch()
        layout.addWidget(button_container)
        
        self.view = QWebEngineView(self)
        try:
            from PyQt6.QtWebEngineCore import QWebEngineProfile
            profile = QWebEngineProfile.defaultProfile()
            self._dashboard_page = _DashboardWebPage(profile, self._on_console_message)
            self.view.setPage(self._dashboard_page)
        except Exception as e:
            print(f"Could not attach console-capture page: {e}")
            self._dashboard_page = None
            
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



    def showEvent(self, event):
        """Log dashboard open by user (for admin dashboard logs)."""
        super().showEvent(event)
        try:
            if self.auth and self.user_id and self.user_role:
                self.auth.log_dashboard_open(self.user_id, self.user_role, action="dashboard_open")
        except Exception as e:
            print(f"Error logging dashboard open: {e}")
    
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
            
            # Map role to dashboard path (superuser has own dashboard + can view others)
            role_paths = {
                "superuser": "dashboard-superuser",
                "superadmin": "dashboard-superadmin",
                "admin": "dashboard-admin",
                "teacher": "dashboard-teacher"
            }
            
            dashboard_path = role_paths.get(self.user_role.lower(), "dashboard-admin")
            
            # Dashboard at abhinavpaudel.com; API at api.abhinavpaudel.com
            base_url = os.getenv("DASHBOARD_URL", "https://abhinavpaudel.com")
            
            # Remove trailing slash if present
            base_url = base_url.rstrip('/')
            
            # Construct full URL with query parameters
            dashboard_url = f"{base_url}/{dashboard_path}?token={urllib.parse.quote(token)}&deviceId={urllib.parse.quote(device_id)}"
            
            return dashboard_url
        except Exception as e:
            print(f"Error building dashboard URL: {e}")
            return None

    def _on_console_message(self, level, message, line_number, source_id):
        """Capture JS console messages from the dashboard (log, warn, error)."""
        level_str = {0: "info", 1: "warning", 2: "error"}.get(level, "info")
        line = f"[{datetime.now().strftime('%H:%M:%S')}] [{level_str}] {message}"
        if source_id:
            line += f" ({source_id}:{line_number})"
        self._console_log.append(line)
        if len(self._console_log) > self._console_log_max:
            self._console_log.pop(0)

    def _show_debug_log(self):
        """Open a dialog showing captured dashboard console messages (API errors, etc.)."""
        dlg = QDialog(self)
        dlg.setWindowTitle("Dashboard debug log")
        dlg.setMinimumSize(700, 400)
        dlg.resize(800, 500)
        layout = QVBoxLayout(dlg)
        text = QPlainTextEdit(dlg)
        text.setReadOnly(True)
        text.setPlaceholderText("Console messages from the dashboard will appear here after you use it.")
        text.setStyleSheet("font-family: Consolas, monospace; font-size: 12px;")
        if self._console_log:
            text.setPlainText("\n".join(self._console_log))
        else:
            text.setPlainText("No messages yet. Use the dashboard (e.g. open teacher dashboard); API errors and console output will appear here.")
        layout.addWidget(text)
        btn = QPushButton("Copy all")
        btn.clicked.connect(lambda: QApplication.clipboard().setText(text.toPlainText()))
        layout.addWidget(btn)
        close_btn = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        close_btn.rejected.connect(dlg.close)
        layout.addWidget(close_btn)
        dlg.exec()

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
