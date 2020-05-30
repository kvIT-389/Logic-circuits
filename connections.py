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
        self.r = self.default_r

        self._terminal = QPainterPath()
        self._terminal.addEllipse(cx - self.r, cy - self.r,
                                  2*self.r, 2*self.r)
        self._wire = wire

        self._type = type_   # "i" - input; "o" - output 
        self.links = []
        self.condition = False   # False - inactive; True - active 

    def draw(self, painter):
        color = Palette.element.contact[self.condition]

        pen = QPen(color, 6, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        brush = QBrush(color)

        painter.strokePath(self._wire, pen)

        if self.links:
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
        self.r *= q
        self._cx *= q
        self._cy *= q

    def move_to(self, new_cx, new_cy):
        self._element.move(
            self._element.x() + (new_cx - self.abs_cx), 
            self._element.y() + (new_cy - self.abs_cy)
        )

    def try_to_connect_to(self, contact):
        dx = contact.abs_cx - self.abs_cx
        dy = contact.abs_cy - self.abs_cy

        if dx*dx + dy*dy <= (self.r + contact.r) ** 2:
            self.move_to(contact.abs_cx, contact.abs_cy)

            self.connect_to(contact)

    def connect_to(self, contact):
        self_link = self._add_link(contact)
        contact_link = contact._add_link(self)

        self_link.trackback = contact_link
        contact_link.trackback = self_link

        contact.element.upd()

    def _add_link(self, link_contact):
        new_link = Link(link_contact)
        self.links.append(new_link)

        return new_link

    def receive_signals(self):
        if "i" in self._type:
            for link in self.links:
                if "o" in link.contact._type and link.contact.condition:
                    self.condition = True
                    break
            else:
                self.condition = False

    def transmit_signal(self):
        if "o" in self._type:
            for link in self.links:
                link.contact.receive_signals()
                link.element.upd()

    def clear_links(self, unaffected_elements):
        remaining_links = []

        for link in self.links:
            if link.element in unaffected_elements:
                remaining_links.append(link)
            else:
                link.contact.links.remove(link.trackback)
                link.element.upd()

        self.links = remaining_links

    @property
    def element(self):
        return self._element

    @property
    def cx(self):
        return self._cx

    @property
    def cy(self):
        return self._cy

    @property
    def abs_cx(self):
        return self._element.x() + round(self._cx)

    @property
    def abs_cy(self):
        return self._element.y() + round(self._cy)

class WireContact(Contact):
    def __init__(self, element, cx, cy):
        # Type of WireContact is "io", 
        # i.e. and input, and output at the same time. 
        Contact.__init__(self, element, "io", cx, cy, None)

    def draw(self, painter):
        r = int(self.r)
        painter.drawEllipse(self._cx - r, self._cy - r, 2*r, 2*r)

    def move_to(self, new_cx, new_cy):
        self._cx = new_cx
        self._cy = new_cy

class WireSegment:
    def __init__(self, wire, *contacts):
        self._wire = wire
        self._contacts = contacts

    def draw(self, painter):
        painter.drawLine(
            self._contacts[0].cx, self._contacts[0].cy, 
            self._contacts[1].cx, self._contacts[1].cy
        )

class Link:
    def __init__(self, contact):
        self.contact = contact
        self.element = contact.element
        self.trackback = None
