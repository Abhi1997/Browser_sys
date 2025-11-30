import sys
from PyQt6.QtWidgets import QApplication
from browser import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("SimpleBrowser")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
