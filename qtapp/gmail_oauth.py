"""
Gmail OAuth Integration for PyQt6
Handles OAuth 2.0 authentication flow with Google
"""

import os
import json
from urllib.parse import urlparse, parse_qs
from PyQt6.QtCore import QUrl, QObject, pyqtSignal
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QProgressBar, QWidget,
    QPushButton, QHBoxLayout, QMessageBox, QLineEdit, QApplication
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QCursor
from authentication import Authentication

try:
    import requests
except ImportError:
    requests = None

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
            self.auth_failed.emit(
                "Gmail OAuth is not configured.\n\n"
                "Please set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET environment variables.\n"
                "Contact your administrator for assistance."
            )
            return None
        
        # Check network connectivity first
        try:
            import socket
            socket.create_connection(("8.8.8.8", 53), timeout=3)
        except (socket.error, OSError):
            self.auth_failed.emit(
                "No internet connection detected.\n\n"
                "Gmail login requires an active internet connection.\n"
                "Please check your network and try again."
            )
            return None
        
        dialog = QDialog(parent)
        dialog.setWindowTitle("Sign in with Google - DCES")
        dialog.setMinimumSize(700, 750)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
            }
        """)
        
        layout = QVBoxLayout(dialog)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header = QLabel("Sign in with Google")
        header.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #1f2937;
            padding: 10px;
        """)
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        # Subtitle
        subtitle = QLabel("Select your Google account to continue")
        subtitle.setStyleSheet("""
            font-size: 14px;
            color: #6b7280;
            padding-bottom: 10px;
        """)
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)
        
        # Progress indicator (initially hidden)
        self.progress_label = QLabel("Connecting to Google...")
        self.progress_label.setStyleSheet("""
            font-size: 12px;
            color: #3b82f6;
            padding: 5px;
        """)
        self.progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.progress_label.hide()
        layout.addWidget(self.progress_label)
        
        # Web view for OAuth
        web_view = QWebEngineView()
        web_view.setStyleSheet("border: 1px solid #e5e7eb; border-radius: 5px;")
        layout.addWidget(web_view)
        
        # Status label
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("""
            font-size: 11px;
            color: #6b7280;
            padding: 5px;
            min-height: 20px;
        """)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        
        # Cancel button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #f3f4f6;
                color: #374151;
                border: 1px solid #d1d5db;
                padding: 8px 20px;
                border-radius: 5px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #e5e7eb;
            }
        """)
        cancel_btn.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        # Build OAuth URL
        auth_url = (
            f"https://accounts.google.com/o/oauth2/v2/auth?"
            f"client_id={self.client_id}&"
            f"redirect_uri={self.redirect_uri}&"
            f"response_type=code&"
            f"scope=openid email profile&"
            f"access_type=offline&"
            f"prompt=select_account"
        )
        
        def handle_url_changed(url):
            url_str = url.toString()
            
            # Update status based on URL
            if "accounts.google.com" in url_str:
                self.status_label.setText("Please sign in with your Google account...")
            elif "localhost:8080/callback" in url_str:
                self.status_label.setText("Processing authentication...")
                self.progress_label.show()
                
                # Extract authorization code
                parsed = urlparse(url_str)
                params = parse_qs(parsed.query)
                code = params.get("code", [None])[0]
                
                if code:
                    # Exchange code for token
                    self._handle_oauth_code(code, dialog, web_view)
                else:
                    error = params.get("error", ["Unknown error"])[0]
                    error_description = params.get("error_description", [""])[0]
                    error_msg = f"Authentication was cancelled or failed: {error}"
                    if error_description:
                        error_msg += f"\n{error_description}"
                    self.auth_failed.emit(error_msg)
                    dialog.reject()
            else:
                self.status_label.setText("")
        
        def handle_load_started():
            self.status_label.setText("Loading...")
        
        def handle_load_finished(ok):
            if ok:
                self.status_label.setText("")
            else:
                self.status_label.setText("Failed to load page. Please check your connection.")
        
        web_view.urlChanged.connect(handle_url_changed)
        web_view.loadStarted.connect(handle_load_started)
        web_view.loadFinished.connect(handle_load_finished)
        
        # Load OAuth URL
        web_view.setUrl(QUrl(auth_url))
        
        return dialog
    
    def _handle_oauth_code(self, code, dialog, web_view):
        """Handle OAuth authorization code"""
        try:
            try:
                import requests
            except ImportError:
                self.auth_failed.emit(
                    "Missing required library.\n\n"
                    "Please install the 'requests' library:\n"
                    "pip install requests"
                )
                dialog.reject()
                return
            
            # Update UI
            self.progress_label.setText("Exchanging authorization code...")
            
            # Exchange code for token
            token_url = "https://oauth2.googleapis.com/token"
            data = {
                "code": code,
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "redirect_uri": self.redirect_uri,
                "grant_type": "authorization_code"
            }
            
            try:
                response = requests.post(token_url, data=data, timeout=15)
                response.raise_for_status()
                token_data = response.json()
            except requests.exceptions.Timeout:
                self.auth_failed.emit(
                    "Request timed out.\n\n"
                    "The connection to Google took too long.\n"
                    "Please check your internet connection and try again."
                )
                dialog.reject()
                return
            except requests.exceptions.RequestException as e:
                self.auth_failed.emit(
                    f"Network error during authentication.\n\n"
                    f"Error: {str(e)}\n\n"
                    f"Please check your internet connection and try again."
                )
                dialog.reject()
                return
            
            if "access_token" not in token_data:
                error_msg = token_data.get("error_description", "Failed to obtain access token")
                error_code = token_data.get("error", "unknown_error")
                self.auth_failed.emit(
                    f"Authentication failed.\n\n"
                    f"Error: {error_msg}\n"
                    f"Error code: {error_code}\n\n"
                    f"Please try again or contact support if the problem persists."
                )
                dialog.reject()
                return
            
            # Update UI
            self.progress_label.setText("Retrieving user information...")
            
            # Get user info
            user_info_url = "https://www.googleapis.com/oauth2/v2/userinfo"
            headers = {"Authorization": f"Bearer {token_data['access_token']}"}
            
            try:
                user_response = requests.get(user_info_url, headers=headers, timeout=10)
                user_response.raise_for_status()
                user_data = user_response.json()
            except requests.exceptions.RequestException as e:
                self.auth_failed.emit(
                    f"Failed to retrieve user information.\n\n"
                    f"Error: {str(e)}\n"
                    f"Please try again."
                )
                dialog.reject()
                return
            
            gmail = user_data.get("email")
            if not gmail:
                self.auth_failed.emit(
                    "Could not retrieve email address from Google account.\n\n"
                    "Please ensure your Google account has an email address and try again."
                )
                dialog.reject()
                return
            
            # Update UI
            self.progress_label.setText(f"Validating account: {gmail}...")
            
            # Validate user in database
            result = self.auth.validate_gmail_user(gmail)
            if result:
                role, user_id = result
                self.progress_label.setText("Authentication successful!")
                # Small delay to show success message
                QTimer.singleShot(500, lambda: dialog.accept())
                self.auth_success.emit(gmail, role, user_id)
            else:
                self.auth_failed.emit(
                    f"Account not authorized.\n\n"
                    f"The email {gmail} is not registered in the system or has not been approved.\n\n"
                    f"Please contact your administrator to request access."
                )
                dialog.reject()
                
        except Exception as e:
            self.auth_failed.emit(
                f"An unexpected error occurred.\n\n"
                f"Error: {str(e)}\n\n"
                f"Please try again or contact support if the problem persists."
            )
            dialog.reject()


class GmailLoginWindow(QDialog):
    """Login window with Gmail OAuth option"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("DCES - Login")
        self.setFixedSize(450, 500)
        # Add DCES styling to window
        self.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
                border: 2px solid #e5e7eb;
                border-radius: 10px;
            }
        """)
        self.login_successful = False
        self.user_role = None
        self.username = None
        self.user_id = None
        self.gmail = None
        
        from PyQt6.QtWidgets import QVBoxLayout, QPushButton, QLabel, QLineEdit, QMessageBox, QWidget
        from PyQt6.QtCore import Qt
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # DCES Logo/Header
        logo_container = QWidget()
        logo_layout = QVBoxLayout(logo_container)
        logo_layout.setContentsMargins(0, 0, 0, 0)
        logo_layout.setSpacing(5)
        
        # DCES Logo Text
        dces_logo = QLabel("DCES")
        dces_logo.setStyleSheet("""
            font-size: 42px;
            font-weight: bold;
            color: #1e40af;
            padding: 15px;
            background-color: #eff6ff;
            border: 3px solid #3b82f6;
            border-radius: 10px;
        """)
        dces_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_layout.addWidget(dces_logo)
        
        # Subtitle
        subtitle = QLabel("Distraction Control Education System")
        subtitle.setStyleSheet("font-size: 11px; color: #6b7280; font-weight: normal;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_layout.addWidget(subtitle)
        
        layout.addWidget(logo_container)
        
        # Title
        title = QLabel("Secure Academic Browser")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #1f2937; margin-top: 10px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        signin_label = QLabel("Sign in to continue")
        signin_label.setStyleSheet("font-size: 12px; color: #6b7280;")
        signin_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(signin_label)
        
        layout.addSpacing(20)
        
        # Username/password fields (fallback)
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        self.username_input.returnPressed.connect(self.handle_password_login)  # Enter key triggers login
        layout.addWidget(self.username_input)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.returnPressed.connect(self.handle_password_login)  # Enter key triggers login
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

        # Forgot password link
        self.forgot_btn = QPushButton("Forgot password?")
        self.forgot_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.forgot_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #3b82f6;
                border: none;
                font-size: 12px;
                text-decoration: underline;
            }
            QPushButton:hover { color: #2563eb; }
        """)
        self.forgot_btn.setFlat(True)
        self.forgot_btn.clicked.connect(self.show_forgot_password_dialog)
        layout.addWidget(self.forgot_btn)

        # Gmail login button (moved below Login button)
        self.gmail_button = QPushButton("Login with Gmail")
        self.gmail_button.setMinimumHeight(40)
        
        # Check if OAuth is configured
        oauth_configured = bool(os.getenv("GOOGLE_CLIENT_ID", ""))
        
        if oauth_configured:
            self.gmail_button.setStyleSheet("""
                QPushButton {
                    background-color: #4285f4;
                    color: white;
                    border: none;
                    padding: 10px 20px;
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
                QPushButton:disabled {
                    background-color: #9ca3af;
                    color: #ffffff;
                }
            """)
        else:
            self.gmail_button.setEnabled(False)
            self.gmail_button.setToolTip("Gmail OAuth is not configured. Please set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET.")
            self.gmail_button.setStyleSheet("""
                QPushButton {
                    background-color: #9ca3af;
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 5px;
                    font-size: 14px;
                    font-weight: bold;
                    min-width: 200px;
                }
                QPushButton:disabled {
                    background-color: #9ca3af;
                    color: #ffffff;
                }
            """)
        
        self.gmail_button.clicked.connect(self.handle_gmail_login)
        layout.addWidget(self.gmail_button)
        
        # Show info if OAuth not configured
        if not oauth_configured:
            oauth_info = QLabel("Gmail login is not available (OAuth not configured)")
            oauth_info.setStyleSheet("""
                font-size: 10px;
                color: #9ca3af;
                font-style: italic;
                padding: 5px;
            """)
            oauth_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(oauth_info)
        
        # Authentication instance - use environment variables
        self.auth = Authentication(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", ""),
            database=os.getenv("DB_NAME", "edubrowser")
        )
        
        # Gmail OAuth handler
        self.oauth = GmailOAuth(self.auth)
        self.oauth.auth_success.connect(self.on_oauth_success)
        self.oauth.auth_failed.connect(self.on_oauth_failed)
    
    def handle_gmail_login(self):
        """Start Gmail OAuth flow"""
        # Disable button during OAuth
        self.gmail_button.setEnabled(False)
        self.gmail_button.setText("Connecting...")
        
        dialog = self.oauth.authenticate(self)
        if dialog:
            result = dialog.exec()
            # Re-enable button after dialog closes
            self.gmail_button.setEnabled(True)
            self.gmail_button.setText("Login with Gmail")
        else:
            # Re-enable button if dialog creation failed
            self.gmail_button.setEnabled(True)
            self.gmail_button.setText("Login with Gmail")
    
    def on_oauth_success(self, gmail, role, user_id):
        """Handle successful OAuth authentication"""
        self.login_successful = True
        self.user_role = role
        self.username = gmail.split("@")[0]  # Use email prefix as username
        self.user_id = user_id
        self.gmail = gmail
        
        # Register device
        try:
            device_info = self.auth.get_device_info()
            self.auth.register_device(user_id, device_info)
        except Exception as e:
            # Log but don't fail login if device registration fails
            print(f"Warning: Device registration failed: {e}")
        
        # Show success message
        QMessageBox.information(
            self,
            "Login Successful",
            f"Welcome, {gmail}!\n\n"
            f"Role: {role.capitalize()}\n"
            f"Your session has been authenticated."
        )
        
        self.accept()
    
    def on_oauth_failed(self, error):
        """Handle OAuth failure"""
        QMessageBox.warning(
            self,
            "Authentication Failed",
            error
        )

    def show_forgot_password_dialog(self):
        """Open dialog to request password reset email."""
        if requests is None:
            QMessageBox.warning(
                self,
                "Forgot password",
                "The requests library is required. Install it with: pip install requests"
            )
            return

        # Ensure .env is loaded (in case cwd differs)
        try:
            from pathlib import Path
            from dotenv import load_dotenv
            root = Path(__file__).resolve().parent
            load_dotenv(root / ".env")
        except Exception:
            pass
        # Must use the API host (api.abhinavpaudel.com), not the dashboard (abhinavpaudel.com)
        api_base = (os.getenv("API_BASE_URL") or "https://api.abhinavpaudel.com").rstrip("/")
        forgot_url = f"{api_base}/api/auth/forgot-password"
        dialog = QDialog(self)
        dialog.setWindowTitle("Forgot password")
        dialog.setMinimumWidth(360)
        # Black text on light background so all text is visible
        dialog.setStyleSheet("""
            QDialog { background-color: #ffffff; color: #000000; }
            QLabel { color: #000000; background: transparent; }
            QLineEdit { color: #000000; background-color: #ffffff; border: 1px solid #9ca3af; border-radius: 4px; padding: 6px; }
            QPushButton { color: #000000; background-color: #e5e7eb; border: 1px solid #9ca3af; border-radius: 5px; font-weight: bold; }
            QPushButton:hover { background-color: #d1d5db; }
            QPushButton#sendBtn { background-color: #3b82f6; color: #ffffff; border-color: #2563eb; }
            QPushButton#sendBtn:hover { background-color: #2563eb; color: #ffffff; }
        """)
        dlayout = QVBoxLayout(dialog)
        dlayout.setSpacing(12)

        label = QLabel("Enter the email address registered with your account. We'll send you a link to reset your password.")
        label.setWordWrap(True)
        dlayout.addWidget(label)
        email_edit = QLineEdit()
        email_edit.setPlaceholderText("Registered email address")
        email_edit.setMinimumHeight(36)
        dlayout.addWidget(email_edit)

        send_btn = QPushButton("Send reset link")
        send_btn.setObjectName("sendBtn")
        send_btn.setMinimumHeight(36)

        def do_send():
            email = email_edit.text().strip()
            if not email:
                QMessageBox.warning(dialog, "Forgot password", "Please enter your email address.")
                return
            send_btn.setEnabled(False)
            send_btn.setText("Sending...")
            QApplication.processEvents()
            try:
                r = requests.post(
                    forgot_url,
                    json={"email": email},
                    headers={"Content-Type": "application/json"},
                    timeout=15
                )
                data = r.json() if r.headers.get("content-type", "").startswith("application/json") else {}
                if r.status_code == 200 and data.get("success"):
                    QMessageBox.information(
                        dialog,
                        "Check your email",
                        "If an account exists with this email, you will receive a password reset link shortly. "
                        "Check your inbox and spam folder."
                    )
                    dialog.accept()
                else:
                    err = data.get("error", "Could not send reset link. Try again or contact support.")
                    if r.status_code == 404:
                        err = f"{err}\n\nRequested URL: {forgot_url}\n(If this is not api.abhinavpaudel.com, set API_BASE_URL in .env and restart the app.)"
                    QMessageBox.warning(
                        dialog,
                        "Forgot password",
                        err
                    )
            except requests.exceptions.RequestException as e:
                QMessageBox.warning(
                    dialog,
                    "Forgot password",
                    f"Could not reach the server. Check your connection.\n\n{str(e)}"
                )
            finally:
                send_btn.setEnabled(True)
                send_btn.setText("Send reset link")

        send_btn.clicked.connect(do_send)
        dlayout.addWidget(send_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setMinimumHeight(36)
        cancel_btn.clicked.connect(dialog.reject)
        dlayout.addWidget(cancel_btn)

        dialog.exec()

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

