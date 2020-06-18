import sys
import os.path

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QIcon

from interface import Sandbox, Toolbar

class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        window_height = max(self.screen().geometry().height(), 640) * 0.5
        window_width = window_height * 1.6

        app_dir = os.path.dirname(os.path.abspath(__file__))
        window_icon_path = os.path.join(app_dir, "icon.ico")

        # Creating application interface 

        self.sandbox = Sandbox(self, round(window_height * 0.0011, 1))
        self.toolbar = Toolbar(self.sandbox, window_height * 0.145)

        # Window setting 

        self.setMinimumSize(window_width, window_height)
        self.setGeometry(
            window_width * 0.34, window_height * 0.37, 
            window_width, window_height
        )

        self.setWindowTitle("Logic circuits")
        self.setWindowIcon(QIcon(window_icon_path))
        self.setStyleSheet("background-color: #f0f0f0;")

        self.show()

    def keyPressEvent(self, event):
        # DELETE pressed 
        if event.nativeVirtualKey() == 46:
            sandbox = self.sandbox

            if event.modifiers() == Qt.ShiftModifier:
                sandbox.clear()
            else:
                for element in sandbox.elements:
                    if element.hover:
                        sandbox.remove_element(element)
                        break
                else:
                    sandbox.remove_elements_group(True)

        # Arrow key pressed 
        elif event.nativeVirtualKey() in [37, 38, 39, 40]:
            for element in self.sandbox.elements:
                if element.hover:
                    keys = {37: -90, 38: 180, 39: 90, 40: 180}
                    element.rotate(keys[event.nativeVirtualKey()])

                    break

    def resizeEvent(self, event):
        self.sandbox.resize(self.width(), self.height())
        self.toolbar.move(0, self.height() - self.toolbar.height())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())
