import sys
from browser import MainWindow
from unittest.mock import MagicMock
from PyQt6.QtWidgets import QApplication

app = QApplication(sys.argv)
mw = MainWindow(auth=MagicMock(), user_role="student", username="test", user_id=1, gmail="t@t.com")

def test_isinstance():
    try:
        from browser import MainWindow as LocalMainWindow
        print("isinstance with LocalMainWindow:", isinstance(mw, LocalMainWindow))
    except Exception as e:
        print("Error:", e)

test_isinstance()
sys.exit(0)
