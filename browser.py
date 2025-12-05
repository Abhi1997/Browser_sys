import sys
from PyQt6.QtCore import QUrl, QSize, Qt
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QPushButton, QLineEdit, 
    QTabWidget, QApplication, QToolBar, QStatusBar, QComboBox, QMessageBox,QDialog
)
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl, QSize, Qt
from PyQt6.QtWidgets import (
    QMainWindow,QInputDialog, QWidget, QVBoxLayout, QLineEdit,QLabel,QLineEdit,QPushButton,QMessageBox,
    QTabWidget, QToolBar, QStatusBar, QComboBox
)
from PyQt6.QtGui import QAction
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage, QWebEngineProfile
from authentication import Authentication


class BrowserTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)



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
                else:
                    mw.status.showMessage("Failed to load page")



class LoginWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login")
        self.setFixedSize(300, 150)

        # Layout
        layout = QVBoxLayout()

        # Username field
        self.username_label = QLabel("Username:")
        self.username_input = QLineEdit()
        layout.addWidget(self.username_label)
        layout.addWidget(self.username_input)

        # Password field
        self.password_label = QLabel("Password:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)

        # Login button
        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.handle_login)
        layout.addWidget(self.login_button)

        self.setLayout(layout)

        # Authentication instance
        self.auth = Authentication(host="localhost", user="root", password="Innovation", database="edubrowser")

        # Login status
        self.login_successful = False

    def handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Login Failed", "Please enter both username and password.")
            return

        role = self.auth.validate_user(username, password)
        if role:
            QMessageBox.information(self, "Login Successful", f"Welcome, {username}! Role: {role}")
            self.login_successful = True
            self.close()  # Close the login window
        else:
            QMessageBox.warning(self, "Login Failed", "Invalid username or password. Please try again.")
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simple Python Browser")
        self.resize(1200, 800)

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

        # Setup UI Components
        self.setup_toolbar()
        self.setup_menu()

        self.status = QStatusBar()
        self.setStatusBar(self.status)

        # Open initial tab
        self.add_tab()
        self.navigate_home()

    def setup_toolbar(self):
        toolbar = QToolBar("Navigation")
        toolbar.setIconSize(QSize(16, 16))
        self.addToolBar(toolbar)

        # Back
        back_action = QAction("Back", self)
        back_action.triggered.connect(lambda: self.current_view().back())
        toolbar.addAction(back_action)

        # Forward
        forward_action = QAction("Forward", self)
        forward_action.triggered.connect(lambda: self.current_view().forward())
        toolbar.addAction(forward_action)

        # Reload
        reload_action = QAction("Reload", self)
        reload_action.triggered.connect(lambda: self.current_view().reload())
        toolbar.addAction(reload_action)

        # Home
        home_action = QAction("Home", self)
        home_action.triggered.connect(self.navigate_home)
        toolbar.addAction(home_action)

        # URL Bar
        toolbar.addWidget(self.url_bar)

        # Zoom
        toolbar.addWidget(self.zoom_combo)

        # New Tab
        new_tab_action = QAction("+", self)
        new_tab_action.triggered.connect(self.add_tab)
        toolbar.addAction(new_tab_action)

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
        tab = BrowserTab(self)
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

        self.current_view().setUrl(QUrl(url_text))
    def prompt_login(self):
        auth = Authentication(host="localhost", user="root", password="your_password", database="edubrowser")
        while True:
            username, ok = QInputDialog.getText(self, "Login", "Username:")
            if not ok:
                exit()  # Exit if the user cancels the login dialog
            password, ok = QInputDialog.getText(self, "Login", "Password:", QInputDialog.Password)
            if not ok:
                exit()
    
            role = auth.validate_user(username, password)
            if role:
                QMessageBox.information(self, "Login Successful", f"Welcome, {username}! Role: {role}")
                self.user_role = role  # Store the user's role
                break
            else:
                QMessageBox.warning(self, "Login Failed", "Invalid username or password. Please try again.")
    def on_zoom_changed(self, text: str):
        if not self.current_view():
            return
        try:
            value = int(text.strip('%')) / 100.0
            self.current_view().setZoomFactor(value)
        except ValueError:
            pass
