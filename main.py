import sys
import os.path

from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QIcon

from interface import Sandbox, Toolbar

class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        window_height = self.screen().geometry().height() * 0.5
        window_width = window_height * 1.6

        app_dir = os.path.dirname(os.path.abspath(__file__))   # Application directory 
        window_icon_path = os.path.join(app_dir, "icon.ico")

        # Creating application interface 

        self.sandbox = Sandbox(self)
        self.toolbar = Toolbar(self, window_height * 0.145)

        # Window setting 

        self.setMinimumSize(window_width, window_height)
        self.setGeometry(300, 200, window_width, window_height)
        self.setWindowTitle("Logic circuits")
        self.setWindowIcon(QIcon(window_icon_path))
        self.setStyleSheet("background-color: #f0f0f0;")

        self.show()

    def resizeEvent(self, event):
        self.sandbox.resize(self.width(), self.height())
        self.toolbar.move(0, self.height() - self.toolbar.height())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())