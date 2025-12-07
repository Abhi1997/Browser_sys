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

        # Load React app (dev server by default). You can switch to a local build path.
        base = react_url or "http://localhost:3000"
        # Pass user role/username to React via URL params
        url = QUrl(f"{base}/?role={self.role}&user={self.username}")
        self.view.setUrl(url)

class AdminDashboard(QDialog):
    def __init__(self, parent=None, auth: Authentication | None = None):
        super().__init__(parent)
        self.setWindowTitle("Admin Dashboard")
        self.setMinimumSize(600, 400)
        self.auth = auth or Authentication()

        layout = QVBoxLayout(self)

        header = QLabel("Admin Dashboard — Users")
        layout.addWidget(header)

        self.user_list = QListWidget()
        layout.addWidget(self.user_list)

        btn_layout = QHBoxLayout()
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.load_users)
        btn_layout.addWidget(self.refresh_btn)

        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.close)
        btn_layout.addWidget(self.close_btn)

        layout.addLayout(btn_layout)

        self.load_users()

    def load_users(self):
        self.user_list.clear()
        try:
            conn = mysql.connector.connect(**self.auth.db_config)
            cursor = conn.cursor()
            cursor.execute("SELECT id, username, role, last_login, is_active FROM Users ORDER BY id ASC")
            rows = cursor.fetchall()
            for r in rows:
                id_, username, role, last_login, is_active = r
                last = last_login.strftime("%Y-%m-%d %H:%M:%S") if isinstance(last_login, datetime) else (str(last_login) if last_login else "never")
                active = "active" if int(is_active) else "inactive"
                self.user_list.addItem(f"{id_:>3} | {username} | {role} | last_login: {last} | {active}")
            cursor.close()
            conn.close()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load users: {e}")