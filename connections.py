# Contains some classes implementing elements' logic. 

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
        self.condition = False   # False - inactive; True - active 

    def draw(self, painter):
        color = Palette.element.contact[self.condition]

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

    def try_to_connect_to(self, contact):
        dx = (contact._element.x() + round(contact._cx)) - (self._element.x() + round(self._cx))
        dy = (contact._element.y() + round(contact._cy)) - (self._element.y() + round(self._cy))

        if dx ** 2 + dy ** 2 <= (self._r + contact._r) ** 2:
            self._element.move(self._element.x() + dx, 
                               self._element.y() + dy)

            self._connect_to(contact)

    def _connect_to(self, contact):
        self_link = self._add_link(contact)
        contact_link = contact._add_link(self)

        self_link.trackback = contact_link
        contact_link.trackback = self_link

        contact.element.upd()

    def _add_link(self, link_contact):
        new_link = Link(link_contact)
        self._links.append(new_link)

        return new_link

    def receive_signals(self):
        if self._type == "i":
            for link in self._links:
                if link.contact._type == "o" and link.contact.condition:
                    self.condition = True
                    break
            else:
                self.condition = False

    def transmit_signal(self):
        if self._type == "o":
            for link in self._links:
                link.contact.receive_signals()
                link.element.upd()

    def clear_links(self, unaffected_elements):
        remaining_links = []

        for link in self._links:
            if link.element in unaffected_elements:
                remaining_links.append(link)
            else:
                link.contact._links.remove(link.trackback)
                link.element.upd()

        self._links = remaining_links

    @property
    def element(self):
        return self._element

class Link:
    def __init__(self, contact):
        self.contact = contact
        self.element = contact.element
        self.trackback = None
