import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget

app = QApplication(sys.argv)
class MainWindow(QMainWindow):
    pass

mw = MainWindow()
tabs = QTabWidget(mw)
mw.setCentralWidget(tabs)

class Tab(QWidget):
    def get_mw(self):
        return self.window()

t = Tab()
tabs.addTab(t, "T")
mw.show()
print("t.window() class:", t.window().__class__.__name__)
print("isinstance(t.window(), MainWindow):", isinstance(t.window(), MainWindow))
