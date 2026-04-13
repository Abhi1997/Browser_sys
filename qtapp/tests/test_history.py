import os
import sys
from PyQt6.QtWidgets import QApplication
from browser import MainWindow
from authentication import Authentication

app = QApplication(sys.argv)
auth = Authentication()

# Dummy user
user_id = 1
role = "student"
username = "testuser"

window = MainWindow(auth=auth, user_role=role, username=username, user_id=user_id, gmail="test@example.com")
window.show()

# Run for 5 seconds to let the home page load
from PyQt6.QtCore import QTimer
QTimer.singleShot(5000, app.quit)
sys.exit(app.exec())
