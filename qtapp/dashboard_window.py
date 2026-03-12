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
        
        # Create tabs
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        # Original Dashboard Tab
        dashboard_tab = QWidget()
        dash_layout = QVBoxLayout(dashboard_tab)
        dash_layout.setContentsMargins(0, 0, 0, 0)
        
        self.view = QWebEngineView(dashboard_tab)
        try:
            from PyQt6.QtWebEngineCore import QWebEngineProfile
            profile = QWebEngineProfile.defaultProfile()
            self._dashboard_page = _DashboardWebPage(profile, self._on_console_message)
            self.view.setPage(self._dashboard_page)
        except Exception as e:
            print(f"Could not attach console-capture page: {e}")
            self._dashboard_page = None
            
        dash_layout.addWidget(self.view)
        self.tabs.addTab(dashboard_tab, "Live Dashboard")
        
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

        # Local Analytics Tab
        analytics_tab = QWidget()
        analytics_layout = QVBoxLayout(analytics_tab)
        analytics_layout.setContentsMargins(0, 0, 0, 0)
        
        self.analytics_view = QWebEngineView(analytics_tab)
        analytics_layout.addWidget(self.analytics_view)
        
        # Add refresh button for analytics tab
        refresh_btn_container = QWidget()
        refresh_btn_layout = QHBoxLayout(refresh_btn_container)
        refresh_btn_layout.setContentsMargins(10, 5, 10, 5)
        refresh_btn = QPushButton("Refresh Data")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #f3f4f6;
                color: #374151;
                border: 1px solid #d1d5db;
                padding: 5px 15px;
                border-radius: 4px;
                font-size: 13px;
            }
            QPushButton:hover { background-color: #e5e7eb; }
        """)
        refresh_btn.clicked.connect(self._load_analytics)
        refresh_btn_layout.addStretch()
        refresh_btn_layout.addWidget(refresh_btn)
        analytics_layout.addWidget(refresh_btn_container)
        
        self.tabs.addTab(analytics_tab, "Local Analytics")
        self._load_analytics()
        
        # Set window icon
        self.setWindowIcon(QApplication.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon))

    def _load_analytics(self):
        """Load data from database and render charts using Chart.js"""
        # Fetch from database
        try:
            conn = self.auth._get_conn()
            cursor = conn.cursor()
            
            # Fetch violations grouped by type
            cursor.execute("SELECT violation_type, COUNT(*) as count FROM Violations GROUP BY violation_type")
            type_violations = cursor.fetchall() or []
            
            # Fetch violations grouped by mode
            cursor.execute("SELECT current_mode, COUNT(*) as count FROM Violations GROUP BY current_mode")
            mode_violations = cursor.fetchall() or []
            
            # Fetch top 10 blocked domains
            cursor.execute("SELECT attempted_url, COUNT(*) as count FROM Violations GROUP BY attempted_url ORDER BY count DESC LIMIT 10")
            top_urls = cursor.fetchall() or []
            
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Error fetching analytics data: {e}")
            type_violations = []
            mode_violations = []
            top_urls = []
            
        import json
        
        types_labels = json.dumps([v[0] for v in type_violations])
        types_data = json.dumps([v[1] for v in type_violations])
        
        modes_labels = json.dumps([v[0] for v in mode_violations])
        modes_data = json.dumps([v[1] for v in mode_violations])
        
        urls_labels = json.dumps([v[0] for v in top_urls])
        urls_data = json.dumps([v[1] for v in top_urls])
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Analytics</title>
            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background: #f3f4f6; color: #1f2937; padding: 20px; }}
                .dashboard {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px; }}
                .chart-container {{ background: white; border-radius: 8px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); height: 300px; }}
                .full-width {{ grid-column: 1 / -1; height: 350px; }}
                h2 {{ margin-top: 0; font-size: 16px; color: #4b5563; border-bottom: 1px solid #e5e7eb; padding-bottom: 10px; }}
                canvas {{ width: 100% !important; height: calc(100% - 30px) !important; }}
            </style>
        </head>
        <body>
            <h1>Security Analytics Dashboard</h1>
            <div class="dashboard">
                <div class="chart-container">
                    <h2>Violations by Mode</h2>
                    <canvas id="modeChart"></canvas>
                </div>
                <div class="chart-container">
                    <h2>Violations by Type</h2>
                    <canvas id="typeChart"></canvas>
                </div>
                <div class="chart-container full-width">
                    <h2>Top Blocked URLs</h2>
                    <canvas id="urlChart"></canvas>
                </div>
            </div>
            
            <script>
                const commonOptions = {{ responsive: true, maintainAspectRatio: false }};
                
                // Mode Chart
                new Chart(document.getElementById('modeChart'), {{
                    type: 'pie',
                    data: {{
                        labels: {modes_labels},
                        datasets: [{{
                            data: {modes_data},
                            backgroundColor: ['#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#6366f1']
                        }}]
                    }},
                    options: {{ ...commonOptions, plugins: {{ legend: {{ position: 'right' }} }} }}
                }});
                
                // Type Chart
                new Chart(document.getElementById('typeChart'), {{
                    type: 'doughnut',
                    data: {{
                        labels: {types_labels},
                        datasets: [{{
                            data: {types_data},
                            backgroundColor: ['#ef4444', '#f59e0b', '#3b82f6', '#10b981', '#6366f1']
                        }}]
                    }},
                    options: {{ ...commonOptions, plugins: {{ legend: {{ position: 'right' }} }} }}
                }});
                
                // URL Chart
                new Chart(document.getElementById('urlChart'), {{
                    type: 'bar',
                    data: {{
                        labels: {urls_labels},
                        datasets: [{{
                            label: 'Violation Count',
                            data: {urls_data},
                            backgroundColor: '#3b82f6'
                        }}]
                    }},
                    options: {{
                        ...commonOptions,
                        scales: {{
                            y: {{ beginAtZero: true, ticks: {{ precision: 0 }} }}
                        }}
                    }}
                }});
            </script>
        </body>
        </html>
        """
        self.analytics_view.setHtml(html)

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
