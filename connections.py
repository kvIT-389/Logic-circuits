# Contains some classes implementing elements' logic. 

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainterPath, QPen, QBrush

from palette import Palette

class Contact:
    default_r = 10

    def __init__(self, element, type_, cx, cy, wire):
        self.element = element

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
        # new_cx and new_cy is absolute relative to the window. 

        self.element.move(
            self.element.x() + (new_cx - self.abs_cx), 
            self.element.y() + (new_cy - self.abs_cy)
        )

    def try_to_connect_to(self, *contacts):
        for contact in contacts:
            if self.is_overlaid_on(contact):
                self.move_to(contact.abs_cx, contact.abs_cy)
                self.connect_to(contact)

    def is_overlaid_on(self, contact):
        dx = contact.abs_cx - self.abs_cx
        dy = contact.abs_cy - self.abs_cy

        return dx*dx + dy*dy <= (self.r + contact.r) ** 2

    def bind_with(self, contact):
        self.links.append(Link(contact))
        contact.links.append(Link(self))

        self.links[-1].trackback = contact.links[-1]
        contact.links[-1].trackback = self.links[-1]

        contact.element.upd()

    def connect_to(self, contact):
        self.bind_with(contact)

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

    def clear_links(self, unaffected_elements):
        remaining_links = []

        for link in self.links:
            if link.element in unaffected_elements:
                remaining_links.append(link)
            else:
                link.contact.links.remove(link.trackback)
                link.element.upd(update_wire_segments=True)

        self.links = remaining_links

    @property
    def cx(self):
        return self._cx

    @property
    def cy(self):
        return self._cy

    @property
    def abs_cx(self):
        return self.element.x() + round(self._cx)

    @property
    def abs_cy(self):
        return self.element.y() + round(self._cy)

class WireContact(Contact):
    def __init__(self, element, cx, cy):
        # Type of WireContact is "io", 
        # i.e. and input, and output at the same time. 
        Contact.__init__(self, element, "io", cx, cy, None)

        self.segments = []

    def draw(self, painter):
        r = int(self.r)
        painter.drawEllipse(self._cx - r, self._cy - r, 2*r, 2*r)

    def move_to(self, new_cx, new_cy):
        # new_cx and new_cy is absolute relative to the window. 

        self._cx = new_cx - self.element.x()
        self._cy = new_cy - self.element.y()

    def connect_to(self, contact):
        if isinstance(contact, WireContact):
            self.element.join(contact.element)
        else:
            self.bind_with(contact)

    def is_invalid(self):
        # Contact is invalid when it doesn't have any links 
        # and belongs only to one segment. 

        return not self.links and len(self.segments) < 2

class WireSegment:
    def __init__(self, wire, contact_0, contact_1):
        self.wire = wire
        self.contacts = [contact_0, contact_1]

        contact_0.segments.append(self)
        contact_1.segments.append(self)

    def draw(self, painter):
        cx_0 = self.contacts[0].cx
        cy_0 = self.contacts[0].cy
        cx_1 = self.contacts[1].cx
        cy_1 = self.contacts[1].cy
        r = self.contacts[0].r

        kx = -(cx_1 - cx_0 < 0) | (cx_1 - cx_0 > 0)
        ky = -(cy_1 - cy_0 < 0) | (cy_1 - cy_0 > 0)

        painter.drawLine(cx_0 + r*kx, cy_0, cx_1, cy_0)
        painter.drawLine(cx_1, cy_0, cx_1, cy_1 - r*ky)

    def is_invalid(self):
        # Segment is invalid (i.e. it's to be removed) 
        # when at least one its contacts is invalid. 

        for contact in self.contacts:
            if contact.is_invalid():
                return True
        else:
            return False

    def remove(self):
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
        self.trackback = None
