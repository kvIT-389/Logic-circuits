from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainterPath, QPen, QBrush

from palette import Palette

class Contact:
    default_r = 10

    def __init__(self, element, type_, cx, cy, wire):
        self._element = element

        self._cx = cx
        self._cy = cy
        self._r = self.default_r

        self._terminal = QPainterPath()
        self._terminal.addEllipse(cx - self._r, cy - self._r,
                                  2*self._r, 2*self._r)
        self._wire = wire

        self._type = type_   # "i" - input; "o" - output 
        self._links = []
        self._condition = False   # False - inactive; True - active 

    def draw(self, painter):
        color = Palette.element.contact[self._condition]

        pen = QPen(color, 6, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        brush = QBrush(color)

        painter.strokePath(self._wire, pen)

        if self._links:
            painter.strokePath(self._terminal, pen)
        else:
            painter.fillPath(self._terminal, brush)

    @classmethod
    def draw_from_tuple(cls, painter, data):
        # data is a tuple with Contact's type, cx, cy and wire 

        r = cls.default_r

        painter.drawEllipse(data[1] - r, data[2] - r, 2*r, 2*r)
        painter.drawPath(data[3])

    def scale(self, q):
        self._r *= q
        self._cx *= q
        self._cy *= q
