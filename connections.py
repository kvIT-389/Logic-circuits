"""
Contains some classes implementing elements' logic. 
"""

from PyQt5.QtCore import Qt, QRect, QPoint
from PyQt5.QtGui import QPainterPath, QPen, QBrush

from palette import Palette

class Contact:
    default_r = 10

    def __init__(self, element, type_, cx, cy, wire):
        self.element = element

        self.cx = cx
        self.cy = cy
        self.r = self.default_r

        self._terminal = QPainterPath()
        self._terminal.addEllipse(cx - self.r, cy - self.r,
                                  2*self.r, 2*self.r)
        self._wire = wire

        self._type = type_   # "i" - input; "o" - output 
        self.links = set()
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
        self.cx *= q
        self.cy *= q

    def move_to(self, cx, cy):
        """
        Moves contact's element so that its abs_cx and abs_cy 
        will be equal to cx and cy. 
        """

        self.element.move(
            cx - round(self.cx), cy - round(self.cy)
        )

    @property
    def abs_cx(self):
        return self.element.x() + round(self.cx)

    @property
    def abs_cy(self):
        return self.element.y() + round(self.cy)

    def is_overlaid_on(self, contact):
        dx = contact.abs_cx - self.abs_cx
        dy = contact.abs_cy - self.abs_cy

        return dx*dx + dy*dy <= (self.r + contact.r) ** 2


    def try_to_connect_to(self, contacts):
        for contact in contacts:
            if self.is_overlaid_on(contact):
                self.move_to(contact.abs_cx, contact.abs_cy)
                self.connect_to(contact)

    def connect_to(self, contact):
        Link.bind(self, contact)

    def disconnect_from(self, elements):
        for link in list(self.links):
            if link.element in elements:
                link.remove()

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
                if link.element not in self.element.update_stack:
                    link.element.upd(updating_element=self.element)

class WireContact(Contact):
    def __init__(self, element, cx, cy):
        # Type of WireContact is "io", 
        # i.e. and input, and output at the same time. 
        Contact.__init__(self, element, "io", cx, cy, None)

        self.segments = []

    def draw(self, painter):
        r = round(self.r)
        painter.drawEllipse(self.cx - r, self.cy - r, 2*r, 2*r)

    def move_to(self, cx, cy):
        """
        Moves contact to cx and cy relative to the window. 
        """

        self.cx = cx - self.element.x()
        self.cy = cy - self.element.y()

    def connect_to(self, contact):
        if isinstance(contact, WireContact):
            self.element.join(contact.element)
        else:
            Link.bind(self, contact)

    def is_invalid(self):
        """
        Returns True if contact is invalid, otherwise returns False. 

        WireContact is invalid when it doesn't have any links 
        and belongs only to one segment. 
        """

        return not self.links and len(self.segments) < 2

class WireSegment:
    def __init__(self, wire, contact_0, contact_1):
        self.wire = wire
        self.contacts = [contact_0, contact_1]

        contact_0.segments.append(self)
        contact_1.segments.append(self)

    def draw(self, painter):
        """
        Draws wire's texture - line between its contacts, 
        using painter. 
        """

        cx_0 = self.contacts[0].cx
        cy_0 = self.contacts[0].cy
        cx_1 = self.contacts[1].cx
        cy_1 = self.contacts[1].cy
        r = self.contacts[0].r

        kx = -(cx_1 - cx_0 < 0) | (cx_1 - cx_0 > 0)
        ky = -(cy_1 - cy_0 < 0) | (cy_1 - cy_0 > 0)

        painter.drawLine(cx_0 + r*kx, cy_0, cx_1, cy_0)
        painter.drawLine(cx_1, cy_0, cx_1, cy_1 - r*ky)

    def get_rect(self):
        rect = QRect(
            QPoint(self.contacts[0].abs_cx, self.contacts[0].abs_cy), 
            QPoint(self.contacts[1].abs_cx, self.contacts[1].abs_cy)
        )
        r = self.contacts[0].r

        return rect.normalized().adjusted(-r, -r, r, r)

    def is_invalid(self):
        """
        Returns True if segment is invalid, otherwise returns False. 

        Segment is invalid when at least one its contact is invalid. 
        """

        for contact in self.contacts:
            if contact.is_invalid():
                return True
        else:
            return False

    def remove(self):
        """
        Removes segment and its invalid contacts from its wire. 
        """

        self.wire.segments.remove(self)

        if self.contacts[0].is_invalid():
            self.wire.contacts.remove(self.contacts[0])

        if self.contacts[1].is_invalid():
            self.wire.contacts.remove(self.contacts[1])

        self.contacts[0].segments.remove(self)
        self.contacts[1].segments.remove(self)

class Link:
    def __init__(self, contact):
        self.contact = contact
        self.element = contact.element
        self._trackback = None

    def __eq__(self, other):
        return self.contact is other.contact

    def __hash__(self):
        return hash(self.contact)

    @classmethod
    def bind(cls, contact_0, contact_1):
        link_0 = cls(contact_1)
        link_1 = cls(contact_0)

        contact_0.links.add(link_0)
        contact_1.links.add(link_1)

        link_0._trackback = link_1
        link_1._trackback = link_0

        contact_0.element.upd()

    def remove(self):
        self._trackback.contact.links.remove(self)
        self.contact.links.remove(self._trackback)

        self.element.upd(update_wire_segments=True)
