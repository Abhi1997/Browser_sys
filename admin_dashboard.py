# language: python
# admin_dashboard.py
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QListWidget, QPushButton, QHBoxLayout, QMessageBox
from PyQt6.QtCore import QUrl
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
        self.view = QWebEngineView(self)
        layout = QVBoxLayout(self)
        layout.addWidget(self.view)
        base = react_url or "http://localhost:3000"
        self.view.setUrl(QUrl(f"{base}/?role={self.role}&user={self.username}"))

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