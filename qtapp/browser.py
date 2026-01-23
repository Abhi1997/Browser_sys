import sys
from datetime import datetime
from PyQt6.QtCore import QUrl, QSize, Qt, QTimer
import socket

# Try to import requests, fallback to socket-only check if not available
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QPushButton, QLineEdit, 
    QTabWidget, QApplication, QToolBar, QStatusBar, QComboBox, 
    QMessageBox, QDialog, QStyle, QHBoxLayout, QLabel, QProgressBar,
    QTableWidget, QTableWidgetItem, QHeaderView, QFormLayout, QGroupBox
)
from PyQt6.QtGui import QAction, QIcon, QColor, QPalette
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage, QWebEngineProfile
from authentication import Authentication
from mode_enforcement import ModeEnforcement
from gmail_oauth import GmailLoginWindow


class BrowserTab(QWidget):
    def __init__(self, parent=None, mode_enforcer=None, student_id=None):
        super().__init__(parent)
        self.mode_enforcer = mode_enforcer
        self.student_id = student_id
        self.visit_start = None

        # specific profile setup can be done here, using default for now
        self.profile = QWebEngineProfile.defaultProfile()
        self.page = QWebEnginePage(self.profile)
        self.view = QWebEngineView()
        self.view.setPage(self.page)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.view)

        # Connect signals for URL and Title changes
        self.view.urlChanged.connect(self.on_url_changed)
        self.view.titleChanged.connect(self.on_title_changed)
        self.view.loadFinished.connect(self.on_load_finished)
        self.view.loadStarted.connect(self.on_load_started)

    def on_url_changed(self, qurl: QUrl):
        # Notify the main window to update the URL bar
        parent = self.parent()
        if isinstance(parent, QTabWidget):
            mw = parent.parent()
            try:
                from browser import MainWindow  # local import to avoid forward reference
            except Exception:
                MainWindow = None
            if MainWindow and isinstance(mw, MainWindow):
                mw.url_bar.setText(qurl.toString())

    def on_title_changed(self, title: str):
        # Update the tab text
        parent = self.parent()
        if isinstance(parent, QTabWidget):
            idx = parent.indexOf(self)
            if idx >= 0:
                parent.setTabText(idx, title[:20] + "..." if len(title) > 20 else title)

    def on_load_started(self):
        """Track when page load starts"""
        self.visit_start = datetime.now()

    def on_load_finished(self, ok: bool):
        # Update status bar via Main Window
        parent = self.parent()
        if isinstance(parent, QTabWidget):
            mw = parent.parent()
            try:
                from browser import MainWindow
            except Exception:
                MainWindow = None
            if MainWindow and isinstance(mw, MainWindow):
                if ok:
                    mw.status.showMessage(f"Loaded: {self.view.title()}")
                    # Log activity if student
                    if self.student_id and self.visit_start:
                        duration = (datetime.now() - self.visit_start).seconds
                        url = self.view.url().toString()
                        if mw.current_mode and mw.user_id:
                            self.mode_enforcer.log_activity(
                                self.student_id, mw.user_id, url, 
                                mw.current_mode, duration
                            )
                else:
                    mw.status.showMessage("Failed to load page")



# LoginWindow is now in gmail_oauth.py - keeping for backward compatibility
LoginWindow = GmailLoginWindow


# Import dashboard and management windows from separate modules
from dashboard_window import DashboardWindow
from management_window import ManagementWindow


class LoadingScreen(QWidget):
    """Loading screen shown after login"""
    def __init__(self, parent=None):
        super().__init__(parent)
        # Set background color to white
        self.setStyleSheet("background-color: #ffffff;")
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.label = QLabel("Loading Secure Browser...")
        self.label.setStyleSheet("font-size: 18px; font-weight: bold; color: #1f2937; background-color: transparent;")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label)
        
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)  # Indeterminate
        self.progress.setStyleSheet("""
            QProgressBar {
                border: 2px solid #e5e7eb;
                border-radius: 5px;
                text-align: center;
                height: 20px;
                background-color: #f3f4f6;
            }
            QProgressBar::chunk {
                background-color: #3b82f6;
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.progress)


class MainWindow(QMainWindow):
    def __init__(self, auth=None, user_role=None, username=None, user_id=None, gmail=None):
        super().__init__()
        self.setWindowTitle("Secure Academic Browser")
        self.resize(1200, 800)

        # Use environment variables for Hostinger database or provided auth
        import os
        self.auth = auth or Authentication(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", ""),
            database=os.getenv("DB_NAME", "edubrowser")
        )
        self.user_role = user_role
        self.username = username
        self.user_id = user_id
        self.gmail = gmail
        
        # Mode enforcement
        self.mode_enforcer = ModeEnforcement(self.auth)
        self.current_mode = None
        self.student_id = None
        
        # Get student mode if student
        if self.user_role == "student":
            self.current_mode = self.auth.get_student_mode(self.user_id)
            self.student_id = self.username  # Use username as student_id
        
        # Show loading screen
        self.loading_screen = LoadingScreen(self)
        self.setCentralWidget(self.loading_screen)
        
        # Setup UI after delay (simulate loading)
        QTimer.singleShot(1500, self.finish_loading)

    def finish_loading(self):
        """Complete loading and show browser UI"""
        # Tab Widget
        self.tabs = QTabWidget(movable=True, tabsClosable=True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.tab_changed)
        self.setCentralWidget(self.tabs)

        # URL Bar
        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Enter URL and press Enter...")
        self.url_bar.returnPressed.connect(self.navigate_to_url)

        # Zoom Controls
        self.zoom_combo = QComboBox()
        self.zoom_combo.addItems(["50%", "75%", "100%", "125%", "150%", "200%"])
        self.zoom_combo.setCurrentText("100%")
        self.zoom_combo.currentTextChanged.connect(self.on_zoom_changed)

        # Initialize network status first (before toolbar setup)
        self.is_online = False
        self.dashboard_action = None
        
        # Setup UI Components
        self.setup_toolbar()
        self.setup_menu()
        self.setup_mode_indicators()

        self.status = QStatusBar()
        self.setStatusBar(self.status)
        
        # Network status indicator
        self.network_status_label = QLabel()
        self.network_status_label.setStyleSheet("padding: 0 10px;")
        self.status.addPermanentWidget(self.network_status_label)
        
        # Check network status
        self.check_network_status()
        
        # Setup network status checker timer (check every 10 seconds)
        self.network_timer = QTimer()
        self.network_timer.timeout.connect(self.check_network_status)
        self.network_timer.start(10000)  # Check every 10 seconds
        
        self.update_security_status()

        # Open initial tab
        self.add_tab()
        self.navigate_home()

    def setup_toolbar(self):
        toolbar = QToolBar("Navigation")
        toolbar.setIconSize(QSize(20, 20))
        self.addToolBar(toolbar)

        style = QApplication.style()

        # Back
        back_action = QAction(style.standardIcon(QStyle.StandardPixmap.SP_ArrowBack), "", self)
        back_action.setToolTip("Back")
        back_action.triggered.connect(lambda: self.current_view() and self.current_view().back())
        toolbar.addAction(back_action)

        # Forward
        fwd_action = QAction(style.standardIcon(QStyle.StandardPixmap.SP_ArrowForward), "", self)
        fwd_action.setToolTip("Forward")
        fwd_action.triggered.connect(lambda: self.current_view() and self.current_view().forward())
        toolbar.addAction(fwd_action)

        # Reload
        reload_action = QAction(style.standardIcon(QStyle.StandardPixmap.SP_BrowserReload), "", self)
        reload_action.setToolTip("Reload")
        reload_action.triggered.connect(lambda: self.current_view() and self.current_view().reload())
        toolbar.addAction(reload_action)

        # Home
        home_action = QAction(style.standardIcon(QStyle.StandardPixmap.SP_DirHomeIcon), "", self)
        home_action.setToolTip("Home")
        home_action.triggered.connect(self.navigate_home)
        toolbar.addAction(home_action)

        # URL Bar
        toolbar.addWidget(self.url_bar)

        # Zoom
        self.zoom_combo.setToolTip("Zoom")
        toolbar.addWidget(self.zoom_combo)

        # New Tab
        new_tab_action = QAction(style.standardIcon(QStyle.StandardPixmap.SP_FileDialogNewFolder), "", self)
        new_tab_action.setToolTip("New Tab")
        new_tab_action.triggered.connect(self.add_tab)
        toolbar.addAction(new_tab_action)

        # Dashboard button (only for admin, superadmin, and teacher)
        if self.user_role in ("admin", "superadmin", "teacher"):
            self.dashboard_action = QAction(style.standardIcon(QStyle.StandardPixmap.SP_ComputerIcon), "", self)
            self.dashboard_action.setToolTip("Open Dashboard")
            self.dashboard_action.triggered.connect(self.open_dashboard)
            toolbar.addAction(self.dashboard_action)
        else:
            self.dashboard_action = None
    
    def setup_mode_indicators(self):
        """Setup mode indicator buttons (for students)"""
        if self.user_role != "student" or not self.current_mode:
            return
        
        mode_toolbar = QToolBar("Mode Indicator")
        mode_toolbar.setMovable(False)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, mode_toolbar)
        
        mode_info = self.mode_enforcer.get_mode_info(self.current_mode)
        
        # Mode label
        mode_label = QLabel(f"{mode_info['icon']} {mode_info['name']}")
        mode_label.setStyleSheet(f"""
            QLabel {{
                background-color: {mode_info['color']};
                color: white;
                padding: 8px 15px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 12px;
            }}
        """)
        mode_label.setToolTip(mode_info['description'])
        mode_toolbar.addWidget(mode_label)
        
        mode_toolbar.addSeparator()
        
        # Info label
        info_label = QLabel("Mode cannot be changed by student")
        info_label.setStyleSheet("color: #374151; font-size: 11px; padding: 5px; background-color: transparent;")
        mode_toolbar.addWidget(info_label)

    def setup_menu(self):
        menubar = self.menuBar()

        # File Menu
        file_menu = menubar.addMenu("&File")

        new_tab_act = QAction("New Tab", self)
        new_tab_act.setShortcut("Ctrl+T")
        new_tab_act.triggered.connect(self.add_tab)
        file_menu.addAction(new_tab_act)

        close_tab_act = QAction("Close Tab", self)
        close_tab_act.setShortcut("Ctrl+W")
        close_tab_act.triggered.connect(lambda: self.close_tab(self.tabs.currentIndex()))
        file_menu.addAction(close_tab_act)

        exit_act = QAction("Exit", self)
        exit_act.setShortcut("Ctrl+Q")
        exit_act.triggered.connect(self.close)
        file_menu.addAction(exit_act)

    def current_tab(self) -> BrowserTab:
        return self.tabs.currentWidget()

    def current_view(self) -> QWebEngineView:
        if self.current_tab():
            return self.current_tab().view
        return None

    def add_tab(self):
        tab = BrowserTab(self, mode_enforcer=self.mode_enforcer, student_id=self.student_id)
        idx = self.tabs.addTab(tab, "New Tab")
        self.tabs.setCurrentIndex(idx)
        self.url_bar.setFocus()

    def close_tab(self, index: int):
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)
        else:
            self.close()  # Close window if last tab is closed

    def tab_changed(self, index):
        if self.current_view():
            url = self.current_view().url().toString()
            self.url_bar.setText(url)

    def navigate_home(self):
        if self.current_view():
            self.current_view().setUrl(QUrl("https://www.google.com"))

    def navigate_to_url(self):
        if not self.current_view():
            return

        url_text = self.url_bar.text().strip()
        if not url_text:
            return

        # Simple sanitization
        if "." not in url_text:
            # Treat as search query if no dot (very basic)
            url_text = f"https://www.google.com/search?q={url_text}"
        elif not url_text.startswith("http://") and not url_text.startswith("https://"):
            url_text = "https://" + url_text

        # Mode enforcement for students
        if self.user_role == "student" and self.current_mode:
            is_allowed, reason = self.mode_enforcer.is_url_allowed(
                url_text, self.current_mode, self.student_id
            )
            
            if not is_allowed:
                self.show_bypass_warning(url_text, reason)
                return

        self.current_view().setUrl(QUrl(url_text))
    
    def show_bypass_warning(self, url, reason):
        """Show security-themed warning for blocked URLs"""
        msg = QMessageBox(self)
        msg.setWindowTitle("⚠️ Security Alert - Access Denied")
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setText("🚫 UNAUTHORIZED ACCESS ATTEMPT DETECTED")
        msg.setInformativeText(
            f"<b>URL Blocked:</b> {url}<br><br>"
            f"<b>Reason:</b> {reason}<br><br>"
            f"<b>Mode:</b> {self.mode_enforcer.get_mode_info(self.current_mode)['name']}<br><br>"
            f"<font color='red'><b>⚠️ This violation has been logged.</b></font><br>"
            f"Repeated violations may result in disciplinary action."
        )
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #ffffff;
            }
            QMessageBox QLabel {
                color: #1f2937;
                font-size: 12px;
            }
        """)
        msg.exec()
    
    def on_zoom_changed(self, text: str):
        if not self.current_view():
            return
        try:
            value = int(text.strip('%')) / 100.0
            self.current_view().setZoomFactor(value)
        except ValueError:
            pass

    def check_network_status(self):
        """Check network connectivity and update status"""
        try:
            # Try to connect to a reliable server (Google DNS)
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            # Also try HTTP request to verify full connectivity if requests is available
            if HAS_REQUESTS:
                try:
                    requests.get("https://www.google.com", timeout=3)
                    self.is_online = True
                except Exception:
                    self.is_online = False
            else:
                # If requests not available, socket check is sufficient
                self.is_online = True
        except (socket.error, OSError, Exception):
            self.is_online = False
        
        # Update network status indicator
        if self.is_online:
            self.network_status_label.setText("🟢 Online")
            self.network_status_label.setStyleSheet("color: #10b981; font-weight: bold; padding: 0 10px;")
            # Enable dashboard button if user has access
            if self.dashboard_action:
                self.dashboard_action.setEnabled(True)
        else:
            self.network_status_label.setText("🔴 Offline")
            self.network_status_label.setStyleSheet("color: #ef4444; font-weight: bold; padding: 0 10px;")
            # Disable dashboard button when offline
            if self.dashboard_action:
                self.dashboard_action.setEnabled(False)
        
        # Update status message with network info
        self.update_security_status()
    
    def update_security_status(self):
        """Update security status indicator in status bar"""
        network_text = "🟢 Online" if self.is_online else "🔴 Offline"
        if self.user_role == "student" and self.current_mode:
            mode_info = self.mode_enforcer.get_mode_info(self.current_mode)
            self.status.showMessage(
                f"🔒 Security Mode: {mode_info['name']} | "
                f"User: {self.username} | "
                f"Role: {self.user_role.capitalize()} | "
                f"Network: {network_text}"
            )
        else:
            self.status.showMessage(
                f"User: {self.username} | Role: {self.user_role.capitalize()} | Network: {network_text}"
            )

    def open_dashboard(self):
        """Open dashboard window for admin/teacher roles"""
        # Check network status before opening dashboard
        if not self.is_online:
            QMessageBox.warning(
                self, 
                "No Network Connection", 
                "Dashboard requires an active internet connection.\n\n"
                "Please check your network connection and try again."
            )
            return
        
        if self.user_role in ("admin", "superadmin", "teacher"):
            dashboard_window = DashboardWindow(self)
            dashboard_window.show()
        else:
            QMessageBox.information(self, "Access Denied", "Dashboard is only available for administrators and teachers.")