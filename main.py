import sys
from PyQt6.QtWidgets import QApplication
from browser import MainWindow, LoginWindow

def main():
    app = QApplication(sys.argv)

    # Show login window
    login_window = LoginWindow()
    login_window.exec()  # Block until the login window is closed

    # If login is successful, open the browser app and pass auth & role
    if getattr(login_window, "login_successful", False):
        window = MainWindow(auth=login_window.auth, user_role=getattr(login_window, "user_role", None), username=getattr(login_window, "username", None))
        window.show()
        sys.exit(app.exec())
    else:
        sys.exit()

if __name__ == "__main__":
    main()