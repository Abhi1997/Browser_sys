import sys
from PyQt6.QtWidgets import QApplication
from browser import MainWindow, LoginWindow

def main():
    app = QApplication(sys.argv)

    # Show login window
    login_window = LoginWindow()
    login_window.exec()  # Block until the login window is closed

    # If login is successful, open the browser app
    if login_window.login_successful:
        window = MainWindow()
        window.show()
        sys.exit(app.exec())
    else:
        sys.exit()  # Exit the app if login is not successful

if __name__ == "__main__":
    main()