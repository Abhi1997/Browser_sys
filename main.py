import os
import sys
from PyQt6.QtCore import Qt, QCoreApplication
from PyQt6.QtWidgets import QApplication
from browser import MainWindow, LoginWindow

def main():
    # macOS stability flags
    os.environ["QTWEBENGINE_DISABLE_SANDBOX"] = "1"
    os.environ["QT_OPENGL"] = "software"
    os.environ["QT_QUICK_BACKEND"] = "software"
    os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = (
        "--disable-gpu --disable-software-rasterizer --no-sandbox "
        "--disable-features=UseOzonePlatform,VizDisplayCompositor "
        "--js-flags=--max-old-space-size=128 --lite-mode"
    )

    # set before QApplication
    QCoreApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts, True)

    app = QApplication(sys.argv)

    login_window = LoginWindow()
    login_window.exec()

    if getattr(login_window, "login_successful", False):
        window = MainWindow(
            auth=login_window.auth,
            user_role=getattr(login_window, "user_role", None),
            username=getattr(login_window, "username", None),
            user_id=getattr(login_window, "user_id", None),
        )
        window.show()
        sys.exit(app.exec())
    else:
        sys.exit()

if __name__ == "__main__":
    main()