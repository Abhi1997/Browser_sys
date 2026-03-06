import os
import sys
from PyQt6.QtCore import Qt, QCoreApplication
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QSettings
from browser import MainWindow, apply_app_theme
from gmail_oauth import GmailLoginWindow

def main():
    try:
        print("Starting main application...")
        # macOS stability flags
        os.environ["QTWEBENGINE_DISABLE_SANDBOX"] = "1"
        os.environ["QT_OPENGL"] = "software"
        os.environ["QT_QUICK_BACKEND"] = "software"
        os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = (
            "--disable-gpu --disable-software-rasterizer --no-sandbox "
            "--disable-features=UseOzonePlatform,VizDisplayCompositor "
            "--js-flags=--max-old-space-size=128 --lite-mode"
        )

        print("Initializing QApplication...")
        app = QApplication(sys.argv)
        
        # Set exception hook to catch uncaught exceptions
        def exception_hook(exctype, value, traceback):
            print(f"Uncaught exception: {value}")
            import traceback as tb
            error_msg = "".join(tb.format_exception(exctype, value, traceback))
            QMessageBox.critical(None, "Application Error", f"An unexpected error occurred:\n\n{value}\n\n{error_msg}")
            sys.exit(1)
        sys.excepthook = exception_hook

        # Apply saved dark mode (Settings -> Dark mode) so login and browser use it
        dark = QSettings("EduBrowser", "Settings").value("dark_mode", False, type=bool)
        apply_app_theme(dark)
        # Ensure message boxes remain readable when not in dark mode
        if not dark:
            app.setStyleSheet(
                app.styleSheet() +
                " QMessageBox { background-color: #ffffff; color: #000000; } "
                "QMessageBox QLabel { color: #000000; min-width: 280px; } "
                "QMessageBox QPushButton { color: #000000; background-color: #e5e7eb; border: 1px solid #9ca3af; min-width: 80px; }"
            )

        print("Initializing login window...")
        login_window = GmailLoginWindow()
        print("Showing login window (exec)...")
        login_window.exec()
        print(f"Login window closed. Successful: {getattr(login_window, 'login_successful', False)}")

        if getattr(login_window, "login_successful", False):
            window = MainWindow(
                auth=login_window.auth,
                user_role=getattr(login_window, "user_role", None),
                username=getattr(login_window, "username", None),
                user_id=getattr(login_window, "user_id", None),
                gmail=getattr(login_window, "gmail", None),
            )
            window.show()
            sys.exit(app.exec())
        else:
            sys.exit()
    except Exception as e:
        print(f"Fatal error during startup: {e}")
        import traceback
        traceback.print_exc()
        # If QApplication is already created, use QMessageBox
        if QApplication.instance():
            QMessageBox.critical(None, "Fatal Error", f"Failed to start application:\n\n{str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()