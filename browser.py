import sys
from PyQt6.QtCore import QUrl, QSize, Qt
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QPushButton, QLineEdit, 
    QTabWidget, QApplication, QToolBar, QStatusBar, QComboBox, QMessageBox
)
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage, QWebEngineProfile

class BrowserTab(QWidget):
    def __init__(self, url="https://www.google.com"):
        super().__init__()
        self.layout = QVBoxLayout()
        self.webview = QWebEngineView()
        self.webview.setUrl(QUrl(url))
        self.layout.addWidget(self.webview)
        self.setLayout(self.layout)

class BrowserMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt6 Browser")
        self.setGeometry(100, 100, 1200, 800)

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.toolbar = QToolBar()
        self.addToolBar(self.toolbar)

        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.load_url)
        self.toolbar.addWidget(self.url_bar)

        new_tab_action = QAction(QIcon(), "New Tab", self)
        new_tab_action.triggered.connect(self.add_new_tab)
        self.toolbar.addAction(new_tab_action)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self.add_new_tab()

    def add_new_tab(self, url="https://www.google.com"):
        new_tab = BrowserTab(url)
        index = self.tabs.addTab(new_tab, "New Tab")
        self.tabs.setCurrentIndex(index)
        new_tab.webview.urlChanged.connect(lambda qurl, tab=new_tab: self.update_url_bar(qurl, tab))
        new_tab.webview.loadFinished.connect(lambda _, tab=new_tab: self.update_tab_title(tab))

    def load_url(self):
        current_tab = self.tabs.currentWidget()
        url = self.url_bar.text()
        if not url.startswith("http"):
            url = "http://" + url
        current_tab.webview.setUrl(QUrl(url))

    def update_url_bar(self, qurl, tab):
        if tab == self.tabs.currentWidget():
            self.url_bar.setText(qurl.toString())

    def update_tab_title(self, tab):
        index = self.tabs.indexOf(tab)
        title = tab.webview.title()
        self.tabs.setTabText(index, title)
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BrowserMainWindow()
    window.show()
    sys.exit(app.exec())