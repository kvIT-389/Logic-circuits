# Contains widgets used for creating GUI 

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QCursor, QPainter, QPen, QColor

class Sandbox(QWidget):
    def __init__(self, parent):
        QWidget.__init__(self, parent)

        self.show()

class Toolbar(QWidget):
    def __init__(self, parent, height):
        QWidget.__init__(self, parent)

        spacing = round(height * 0.12)
        panel_height = height - 2*spacing
        panel_width = panel_height / ElementPanel.default_height * ElementPanel.default_width

        # Later, strings will be changed to appropriate element constructor 
        elements = "And", "Or", "Xor", "Not", "Switch", "Lamp"

        for n in range(len(elements)):
            new_panel = ElementPanel(self, elements[n])
            new_panel.move(spacing + n *(panel_width + spacing), spacing)
            new_panel.resize(panel_width, panel_height)

        self.resize(len(elements) * (panel_width + spacing) + spacing, height)
        self.show()

class ElementPanel(QWidget):
    default_width = 420
    default_height = 250

    def __init__(self, parent, element_constructor):
        QWidget.__init__(self, parent)

        self.element_constructor = element_constructor

        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.show()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        x_scale = self.width() / self.default_width
        y_scale = self.height() / self.default_height
        painter.scale(x_scale, y_scale)

        pen = QPen(QColor(62, 63, 65), 10, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        painter.setPen(pen)

        painter.drawRoundedRect(5, 5, self.default_width - 10, self.default_height - 10, 40, 40)

        painter.end()

__all__ = [Sandbox, Toolbar]