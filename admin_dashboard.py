# language: python
# admin_dashboard.py
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QListWidget, QPushButton, QHBoxLayout, QMessageBox, QLineEdit
from PyQt6.QtCore import QUrl, Qt
from PyQt6.QtWebEngineWidgets import QWebEngineView
import mysql.connector
from authentication import Authentication
from datetime import datetime

class DashboardWindow(QDialog):
    def __init__(self, parent=None, auth: Authentication | None = None, role: str | None = None, username: str | None = None, react_url: str | None = None):
        super().__init__(parent)
        self.setWindowTitle("Dashboard")
        self.setMinimumSize(900, 600)
        self.auth = auth
        self.role = role or ""
        self.username = username or ""
        
        # Create layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Create web view FIRST (needed for button connections)
        self.view = QWebEngineView(self)
        
        # Create URL bar
        url_layout = QHBoxLayout()
        url_layout.setContentsMargins(0, 0, 0, 0)
        url_label = QLabel("URL:")
        url_label.setMinimumWidth(30)
        url_layout.addWidget(url_label)
        
        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Enter URL or view current URL...")
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        url_layout.addWidget(self.url_bar)
        
        # Navigation buttons
        self.back_btn = QPushButton("◀")
        self.back_btn.setToolTip("Back")
        self.back_btn.setMaximumWidth(30)
        self.back_btn.clicked.connect(self.view.back)
        url_layout.addWidget(self.back_btn)
        
        self.forward_btn = QPushButton("▶")
        self.forward_btn.setToolTip("Forward")
        self.forward_btn.setMaximumWidth(30)
        self.forward_btn.clicked.connect(self.view.forward)
        url_layout.addWidget(self.forward_btn)
        
        self.reload_btn = QPushButton("↻")
        self.reload_btn.setToolTip("Reload")
        self.reload_btn.setMaximumWidth(30)
        self.reload_btn.clicked.connect(self.view.reload)
        url_layout.addWidget(self.reload_btn)
        
        layout.addLayout(url_layout)
        
        # Add web view to layout
        layout.addWidget(self.view)
        
        # Connect URL change signals
        self.view.urlChanged.connect(self.update_url_bar)
        self.view.loadStarted.connect(self.on_load_started)
        self.view.loadFinished.connect(self.on_load_finished)
        
        # If react_url is provided, use it directly (it's already a complete URL with token and deviceId)
        # Otherwise, construct a basic URL
        if react_url:
            url = QUrl(react_url)
        else:
            base = "http://localhost:3000"
            url = QUrl(f"{base}/?role={self.role}&user={self.username}")
        
        self.view.setUrl(url)
    
    def update_url_bar(self, qurl: QUrl):
        """Update the URL bar when the page URL changes"""
        url_string = qurl.toString()
        self.url_bar.setText(url_string)
        # Update window title
        self.setWindowTitle(f"Dashboard - {url_string[:50]}")
    
    def navigate_to_url(self):
        """Navigate to the URL entered in the URL bar"""
        url_text = self.url_bar.text().strip()
        if url_text:
            if not url_text.startswith(('http://', 'https://')):
                url_text = 'http://' + url_text
            url = QUrl(url_text)
            if url.isValid():
                self.view.setUrl(url)
            else:
                QMessageBox.warning(self, "Invalid URL", f"The URL '{url_text}' is not valid.")
    
    def on_load_started(self):
        """Called when page load starts"""
        self.url_bar.setStyleSheet("background-color: #fff3cd;")  # Yellow tint
    
    def on_load_finished(self, success: bool):
        """Called when page load finishes"""
        if success:
            self.url_bar.setStyleSheet("background-color: white;")
        else:
            self.url_bar.setStyleSheet("background-color: #f8d7da;")  # Red tint for errors

# Base list view helper
def _load_users(list_widget, auth: Authentication):
    try:
        conn = mysql.connector.connect(**auth.db_config)
        cur = conn.cursor()
        cur.execute("SELECT id, username, role, last_login, is_active FROM Users ORDER BY id ASC")
        for id_, username, role, last_login, is_active in cur.fetchall():
            last = last_login.strftime("%Y-%m-%d %H:%M:%S") if isinstance(last_login, datetime) else (str(last_login) if last_login else "never")
            active = "active" if int(is_active) else "inactive"
            list_widget.addItem(f"{id_:>3} | {username} | {role} | last_login: {last} | {active}")
        cur.close()
        conn.close()
    except Exception as e:
        QMessageBox.warning(list_widget, "Error", f"Failed to load users: {e}")

class AdminDashboard(QDialog):
    def __init__(self, parent=None, auth: Authentication | None = None):
        super().__init__(parent)
        self.setWindowTitle("Admin Dashboard")
        self.setMinimumSize(600, 400)
        self.auth = auth or Authentication()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Admin — Users"))
        self.user_list = QListWidget()
        layout.addWidget(self.user_list)
        btns = QHBoxLayout()
        refresh = QPushButton("Refresh"); refresh.clicked.connect(self.load_users); btns.addWidget(refresh)
        close = QPushButton("Close"); close.clicked.connect(self.close); btns.addWidget(close)
        layout.addLayout(btns)
        self.load_users()
    def load_users(self): self.user_list.clear(); _load_users(self.user_list, self.auth)

class TeacherDashboard(QDialog):
    def __init__(self, parent=None, auth: Authentication | None = None, username: str | None = None):
        super().__init__(parent)
        self.setWindowTitle("Teacher Dashboard")
        self.setMinimumSize(600, 400)
        self.auth = auth or Authentication()
        self.username = username or ""
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(f"Teacher — {self.username}"))
        self.user_list = QListWidget()
        layout.addWidget(self.user_list)
        btns = QHBoxLayout()
        refresh = QPushButton("Refresh Class"); refresh.clicked.connect(self.load_users); btns.addWidget(refresh)
        close = QPushButton("Close"); close.clicked.connect(self.close); btns.addWidget(close)
        layout.addLayout(btns)
        self.load_users()
    def load_users(self): self.user_list.clear(); _load_users(self.user_list, self.auth)

class SuperAdminDashboard(QDialog):
    def __init__(self, parent=None, auth: Authentication | None = None):
        super().__init__(parent)
        self.setWindowTitle("Super Admin Dashboard")
        self.setMinimumSize(700, 450)
        self.auth = auth or Authentication()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Super Admin — Global Overview"))
        self.user_list = QListWidget()
        layout.addWidget(self.user_list)
        btns = QHBoxLayout()
        refresh = QPushButton("Refresh All"); refresh.clicked.connect(self.load_users); btns.addWidget(refresh)
        close = QPushButton("Close"); close.clicked.connect(self.close); btns.addWidget(close)
        layout.addLayout(btns)
        self.load_users()
    def load_users(self): self.user_list.clear(); _load_users(self.user_list, self.auth)