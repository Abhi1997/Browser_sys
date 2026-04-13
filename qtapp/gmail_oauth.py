"""
Gmail OAuth Integration for PyQt6
Handles OAuth 2.0 authentication flow with Google
"""

import os
import json
from urllib.parse import urlparse, parse_qs
from PyQt6.QtCore import QUrl, QObject, pyqtSignal, QThread
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
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

class OAuthCallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path == '/callback':
            params = parse_qs(parsed_path.query)
            if 'code' in params:
                self.server.oauth_code = params['code'][0]
                self.server.oauth_error = None
                
                # Send success response
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                
                success_html = """
                <html>
                <head>
                    <title>Authentication Successful</title>
                    <link rel="icon" type="image/png" href="/favicon.ico">
                </head>
                <body style='font-family: sans-serif; text-align: center; padding-top: 50px;'>
                    <img src="/favicon.ico" width="80" alt="DCES Logo" style="margin-bottom: 20px;" />
                    <h2>Authentication successful!</h2>
                    <p>You can close this tab and return to the application.</p>
                    <script>window.setTimeout(function(){window.close();}, 3000);</script>
                </body>
                </html>
                """
                self.wfile.write(success_html.encode('utf-8'))
            else:
                self.server.oauth_code = None
                error = params.get('error', ['Unknown error'])[0]
                error_desc = params.get('error_description', [''])[0]
                self.server.oauth_error = f"{error}: {error_desc}"
                
                # Send error response
                self.send_response(400)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                
                error_html = """
                <html>
                <head>
                    <title>Authentication Failed</title>
                    <link rel="icon" type="image/png" href="/favicon.ico">
                </head>
                <body style='font-family: sans-serif; text-align: center; padding-top: 50px; color: red;'>
                    <img src="/favicon.ico" width="80" alt="DCES Logo" style="margin-bottom: 20px;" />
                    <h2>Authentication failed</h2>
                    <p>Please close this tab and try again.</p>
                </body>
                </html>
                """
                self.wfile.write(error_html.encode('utf-8'))
                
        elif parsed_path.path == '/favicon.ico':
            import os
            # Serve the DCES logo as the favicon
            logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logo', 'DCES logo.png')
            if os.path.exists(logo_path):
                self.send_response(200)
                self.send_header('Content-type', 'image/png')
                self.end_headers()
                with open(logo_path, 'rb') as f:
                    self.wfile.write(f.read())
            else:
                self.send_response(404)
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass  # Suppress console logging

class OAuthServerThread(QThread):
    code_received = pyqtSignal(str)
    error_received = pyqtSignal(str)

    def __init__(self, port=8080):
        super().__init__()
        self.port = port
        self.server = None

    def run(self):
        try:
            self.server = HTTPServer(('localhost', self.port), OAuthCallbackHandler)
            self.server.oauth_code = None
            self.server.oauth_error = None
            self.server.timeout = 0.5  # Check for interruption twice a second
            
            while not self.isInterruptionRequested() and self.server.oauth_code is None and self.server.oauth_error is None:
                self.server.handle_request()
            
            if self.server.oauth_code:
                self.code_received.emit(self.server.oauth_code)
            elif self.server.oauth_error:
                self.error_received.emit(self.server.oauth_error)
                
        except Exception as e:
            self.error_received.emit(f"Server error: {str(e)}")
        finally:
            if self.server:
                self.server.server_close()

class GmailOAuth(QObject):
    """Gmail OAuth handler using system default browser"""
    
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
        dialog.setWindowTitle("Sign in with Google")
        dialog.setMinimumSize(400, 200)
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
        
        # Progress indicator
        self.progress_label = QLabel("A new browser window has been opened for Google sign-in.")
        self.progress_label.setStyleSheet("""
            font-size: 14px;
            color: #3b82f6;
            padding: 5px;
        """)
        self.progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.progress_label)
        
        # Status label
        self.status_label = QLabel("Waiting for authentication callback on port 8080...")
        self.status_label.setStyleSheet("""
            font-size: 12px;
            color: #6b7280;
            padding: 5px;
            min-height: 20px;
        """)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        
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
        
        # Start OAuth Background Listener Thread
        self.server_thread = OAuthServerThread(port=8080)
        
        def handle_code(code):
            self.server_thread.quit()
            self._handle_oauth_code(code, dialog)
            
        def handle_error(error_msg):
            self.server_thread.quit()
            self.auth_failed.emit(f"Authentication was cancelled or failed:\n{error_msg}")
            dialog.reject()
            
        self.server_thread.code_received.connect(handle_code)
        self.server_thread.error_received.connect(handle_error)
        self.server_thread.start()
        
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
        
        def on_cancel():
            self.server_thread.requestInterruption()
            self.server_thread.quit()
            dialog.reject()
            
        cancel_btn.clicked.connect(on_cancel)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        # Open System Browser
        webbrowser.open(auth_url)
        
        dialog.finished.connect(lambda: self.server_thread.requestInterruption())
        
        return dialog
    
    def _handle_oauth_code(self, code, dialog):
        """Handle OAuth authorization code returned by system browser"""
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
        self.username_input.setStyleSheet("""
        QLineEdit {
            color: black;  /* text color when typing */
            background-color: lightgrey;
        }

        QLineEdit::placeholder {
            color: black;  /* placeholder text color */
        }
        """)
        self.username_input.returnPressed.connect(self.handle_password_login)  # Enter key triggers login
        layout.addWidget(self.username_input)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setStyleSheet("""
        QLineEdit {
            color: black;  /* text color when typing */
            background-color: lightgrey;
        }

        QLineEdit::placeholder {
            color: black;  /* placeholder text color */
        }
        """)
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
        
        # Check for persistent device-bound session
        from PyQt6.QtCore import QSettings, QTimer
        settings = QSettings("EduBrowser", "Settings")
        saved_fingerprint = settings.value("device_fingerprint", None)
        user_id = settings.value("user_id", None)
        
        if saved_fingerprint and user_id:
            try:
                current_fingerprint = self.auth.get_device_info()["device_fingerprint"]
                login_timestamp = settings.value("login_timestamp", None)
                import time
                expired = False
                if login_timestamp:
                    try:
                        if time.time() - float(login_timestamp) > 4 * 3600:
                            expired = True
                    except:
                        pass
                if saved_fingerprint == current_fingerprint and not expired:
                    # Valid device session
                    self.login_successful = True
                    self.user_role = settings.value("user_role")
                    self.username = settings.value("username")
                    self.user_id = user_id
                    self.gmail = settings.value("gmail")
                    
                    # Accept the dialog immediately in the event loop
                    QTimer.singleShot(0, self.accept)
                else:
                    # Invalid/copied or expired session, wipe it
                    settings.remove("device_fingerprint")
                    settings.remove("user_id")
                    settings.remove("user_role")
                    settings.remove("username")
                    settings.remove("gmail")
                    settings.remove("login_timestamp")
                    try:
                        from PyQt6.QtWebEngineCore import QWebEngineProfile
                        profile = QWebEngineProfile.defaultProfile()
                        profile.cookieStore().deleteAllCookies()
                        profile.clearAllVisitedLinks()
                    except:
                        pass
            except Exception:
                pass
    
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
            
            # Save persistent session to QSettings
            from PyQt6.QtCore import QSettings
            settings = QSettings("EduBrowser", "Settings")
            settings.setValue("user_role", role)
            settings.setValue("username", self.username)
            settings.setValue("user_id", user_id)
            settings.setValue("gmail", gmail)
            settings.setValue("device_fingerprint", device_info["device_fingerprint"])
            import time
            settings.setValue("login_timestamp", time.time())
            
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
        # Prevent double-firing from Enter key + Button clicked
        if getattr(self, "_is_logging_in", False):
            return
        self._is_logging_in = True
        
        try:
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
                
                # Save persistent session to QSettings
                from PyQt6.QtCore import QSettings
                settings = QSettings("EduBrowser", "Settings")
                settings.setValue("user_role", role)
                settings.setValue("username", username)
                settings.setValue("user_id", user_id)
                settings.setValue("gmail", getattr(self, "gmail", None))
                settings.setValue("device_fingerprint", device_info["device_fingerprint"])
                import time
                settings.setValue("login_timestamp", time.time())
                
                QMessageBox.information(self, "Login Successful", 
                                      f"Welcome, {username}! Role: {role}")
                self.accept()
            else:
                QMessageBox.warning(self, "Login Failed", 
                                  "Invalid username or password, or account not approved.")
        finally:
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(200, lambda: setattr(self, "_is_logging_in", False))

