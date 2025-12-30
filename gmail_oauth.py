"""
Gmail OAuth Integration for PyQt6
Handles OAuth 2.0 authentication flow with Google
"""

import os
import json
from urllib.parse import urlparse, parse_qs
from PyQt6.QtCore import QUrl, QObject, pyqtSignal
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QProgressBar
from authentication import Authentication

class GmailOAuth(QObject):
    """Gmail OAuth handler using PyQt6 WebEngine"""
    
    auth_success = pyqtSignal(str, str, int)  # gmail, role, user_id
    auth_failed = pyqtSignal(str)
    
    def __init__(self, auth: Authentication):
        super().__init__()
        self.auth = auth
        self.client_id = os.getenv("GOOGLE_CLIENT_ID", "")
        self.client_secret = os.getenv("GOOGLE_CLIENT_SECRET", "")
        self.redirect_uri = "http://localhost:8080/callback"
        
        if not self.client_id:
            print("Warning: GOOGLE_CLIENT_ID not set. Gmail OAuth will not work.")
    
    def authenticate(self, parent=None):
        """
        Start OAuth authentication flow
        
        Returns: QDialog for OAuth flow
        """
        if not self.client_id:
            self.auth_failed.emit("Gmail OAuth not configured. Please set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET")
            return None
        
        dialog = QDialog(parent)
        dialog.setWindowTitle("Gmail Authentication")
        dialog.setMinimumSize(600, 700)
        
        layout = QVBoxLayout(dialog)
        
        label = QLabel("Sign in with Google")
        label.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px;")
        layout.addWidget(label)
        
        web_view = QWebEngineView()
        layout.addWidget(web_view)
        
        # Build OAuth URL
        auth_url = (
            f"https://accounts.google.com/o/oauth2/v2/auth?"
            f"client_id={self.client_id}&"
            f"redirect_uri={self.redirect_uri}&"
            f"response_type=code&"
            f"scope=openid email profile&"
            f"access_type=offline"
        )
        
        web_view.setUrl(QUrl(auth_url))
        
        def handle_url_changed(url):
            url_str = url.toString()
            if "localhost:8080/callback" in url_str:
                # Extract authorization code
                parsed = urlparse(url_str)
                params = parse_qs(parsed.query)
                code = params.get("code", [None])[0]
                
                if code:
                    # Exchange code for token (simplified - in production, use backend)
                    self._handle_oauth_code(code, dialog)
                else:
                    error = params.get("error", ["Unknown error"])[0]
                    self.auth_failed.emit(f"OAuth error: {error}")
                    dialog.reject()
        
        web_view.urlChanged.connect(handle_url_changed)
        
        return dialog
    
    def _handle_oauth_code(self, code, dialog):
        """Handle OAuth authorization code"""
        try:
            try:
                import requests
            except ImportError:
                self.auth_failed.emit("OAuth requires 'requests' library. Please install: pip install requests")
                dialog.reject()
                return
            
            # Exchange code for token
            token_url = "https://oauth2.googleapis.com/token"
            data = {
                "code": code,
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "redirect_uri": self.redirect_uri,
                "grant_type": "authorization_code"
            }
            
            response = requests.post(token_url, data=data, timeout=10)
            token_data = response.json()
            
            if "access_token" not in token_data:
                error_msg = token_data.get("error_description", "Failed to obtain access token")
                self.auth_failed.emit(f"OAuth error: {error_msg}")
                dialog.reject()
                return
            
            # Get user info
            user_info_url = "https://www.googleapis.com/oauth2/v2/userinfo"
            headers = {"Authorization": f"Bearer {token_data['access_token']}"}
            user_response = requests.get(user_info_url, headers=headers, timeout=10)
            user_data = user_response.json()
            
            gmail = user_data.get("email")
            if not gmail:
                self.auth_failed.emit("Could not retrieve email from Google")
                dialog.reject()
                return
            
            # Validate user
            result = self.auth.validate_gmail_user(gmail)
            if result:
                role, user_id = result
                dialog.accept()
                self.auth_success.emit(gmail, role, user_id)
            else:
                self.auth_failed.emit(f"User {gmail} not found or not approved")
                dialog.reject()
                
        except requests.exceptions.RequestException as e:
            self.auth_failed.emit(f"Network error: {str(e)}")
            dialog.reject()
        except Exception as e:
            self.auth_failed.emit(f"OAuth error: {str(e)}")
            dialog.reject()


class GmailLoginWindow(QDialog):
    """Login window with Gmail OAuth option"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Login - Secure Academic Browser")
        self.setFixedSize(420, 350)
        self.login_successful = False
        self.user_role = None
        self.username = None
        self.user_id = None
        self.gmail = None
        
        from PyQt6.QtWidgets import QVBoxLayout, QPushButton, QLabel, QLineEdit, QMessageBox
        from PyQt6.QtCore import Qt
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("Secure Academic Browser")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #1f2937;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        subtitle = QLabel("Sign in to continue")
        subtitle.setStyleSheet("font-size: 12px; color: #6b7280;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)
        
        layout.addSpacing(20)
        
        # Gmail OAuth button
        self.gmail_button = QPushButton("Sign in with Gmail")
        self.gmail_button.setMinimumHeight(45)
        self.gmail_button.setStyleSheet("""
            QPushButton {
                background-color: #4285f4;
                color: white;
                border: none;
                padding: 12px 20px;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
                min-width: 200px;
            }
            QPushButton:hover {
                background-color: #357ae8;
            }
            QPushButton:pressed {
                background-color: #2d5aa0;
            }
        """)
        self.gmail_button.clicked.connect(self.handle_gmail_login)
        layout.addWidget(self.gmail_button)
        
        # Divider
        divider = QLabel("or")
        divider.setStyleSheet("color: #9ca3af;")
        divider.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(divider)
        
        # Username/password fields (fallback)
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        layout.addWidget(self.username_input)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password_input)
        
        # Login button
        self.login_button = QPushButton("Login")
        self.login_button.setMinimumHeight(40)
        self.login_button.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
                min-width: 200px;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        self.login_button.clicked.connect(self.handle_password_login)
        layout.addWidget(self.login_button)
        
        # Authentication instance
        self.auth = Authentication(
            host="localhost", 
            user="root", 
            password="Innovation", 
            database="edubrowser"
        )
        
        # Gmail OAuth handler
        self.oauth = GmailOAuth(self.auth)
        self.oauth.auth_success.connect(self.on_oauth_success)
        self.oauth.auth_failed.connect(self.on_oauth_failed)
    
    def handle_gmail_login(self):
        """Start Gmail OAuth flow"""
        dialog = self.oauth.authenticate(self)
        if dialog:
            dialog.exec()
    
    def on_oauth_success(self, gmail, role, user_id):
        """Handle successful OAuth authentication"""
        self.login_successful = True
        self.user_role = role
        self.username = gmail.split("@")[0]  # Use email prefix as username
        self.user_id = user_id
        self.gmail = gmail
        
        # Register device
        device_info = self.auth.get_device_info()
        self.auth.register_device(user_id, device_info)
        
        self.accept()
    
    def on_oauth_failed(self, error):
        """Handle OAuth failure"""
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.warning(self, "Authentication Failed", error)
    
    def handle_password_login(self):
        """Handle traditional username/password login"""
        from PyQt6.QtWidgets import QMessageBox
        
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        if not username or not password:
            QMessageBox.warning(self, "Login Failed", 
                             "Please enter both username and password.")
            return
        
        result = self.auth.validate_user_with_id(username, password)
        if result:
            role, user_id = result
            self.login_successful = True
            self.user_role = role
            self.username = username
            self.user_id = user_id
            
            # Register device
            device_info = self.auth.get_device_info()
            self.auth.register_device(user_id, device_info)
            
            QMessageBox.information(self, "Login Successful", 
                                  f"Welcome, {username}! Role: {role}")
            self.accept()
        else:
            QMessageBox.warning(self, "Login Failed", 
                              "Invalid username or password, or account not approved.")

