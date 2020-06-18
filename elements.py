"""
Contains circuit elements widgets for creating circuits. 
"""

from PyQt5.QtCore import Qt, QRect
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QPen, QBrush

from connections import Contact, WireContact, WireSegment

from graphics import Graphics
from palette import Palette

class LogicElement(QWidget):
    default_width = 0
    default_height = 0

    contacts_data = []

    def __init__(self, parent):
        QWidget.__init__(self, parent)

        self.contacts = []
        for data in self.contacts_data:
            self.contacts.append(Contact(self, *data))

        self.scale_value = 1
        self.hover = False

        self.update_stack = []

        self.resize(self.default_width, self.default_height)
        self.show()

    def connect_to(self, elements):
        self.update_condition()

        contacts_to_connect = []
        for element in self.parentWidget().elements:
            if element is not self and element in elements:
                contacts_to_connect.extend(element.contacts)

        for contact in self.contacts:
            contact.try_to_connect_to(contacts_to_connect)

        if isinstance(self, Wire):
            self.update_segments()

    def disconnect_from(self, elements):
        for contact in self.contacts:
            contact.disconnect_from(elements)

            contact.condition = False

        if isinstance(self, (Switch, Lamp)):
            self.update_condition()

    def upd(self, updating_element=None, update_wire_segments=False):
        if update_wire_segments and isinstance(self, Wire):
            self.update_segments()
        else:
            for contact in self.contacts:
                contact.receive_signals()

            self.update_condition()

            if updating_element:
                self.update_stack = [
                    *updating_element.update_stack, updating_element
                ]

            for contact in self.contacts:
                contact.transmit_signal()

            self.update_stack.clear()

            self.update()

    def remove(self):
        self.parentWidget().remove_element(self)

class DraggableElement(LogicElement):
    def __init__(self, parent):
        LogicElement.__init__(self, parent)

        self._rotation = 0   # in degrees 
        self._press_pos = None

        # At the time of creation of new wire (or its new segment), 
        # created_wire stores this new (or already existing) wire. 
        self._created_wire = None

        self.setCursor(Qt.PointingHandCursor)

    # Drawing 

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        self.transform_painter(painter)

        if self.hover:
            pen = QPen(
                Palette.element.border, 3, 
                Qt.DotLine, Qt.RoundCap, Qt.RoundJoin
            )
            painter.setPen(pen)

            painter.drawRect(
                1.5, 1.5, self.default_width - 3, self.default_height - 3
            )

        for contact in self.contacts:
            contact.draw(painter)

        pen = QPen(
            Palette.element.outline, 6, 
            Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin
        )
        self.draw_outline(painter, pen)

        painter.end()

    def transform_painter(self, painter):
        painter.rotate(self._rotation)

        w = self.width()
        h = self.height()
        offsets = [
            (0, 0), (0, -w), (-w, -h), (-h, 0)
        ][self._rotation // 90]

        painter.translate(*offsets)
        painter.scale(self.scale_value, self.scale_value)

    def draw_outline(self, painter, pen):
        painter.strokePath(self.outline, pen)

    @classmethod
    def draw_in_panel(cls, painter, panel_width, panel_height):
        x_offset = (panel_width - cls.default_width) / 2
        y_offset = (panel_height - cls.default_height) / 2

        painter.translate(x_offset, y_offset)

        for data in cls.contacts_data:
            Contact.draw_from_tuple(painter, data)

        painter.drawPath(cls.outline)

    # Mouse events 

    def mousePressEvent(self, event):
        # Left button press 
        if event.button() == 1:
            self._press_pos = event.pos()

            self.disconnect_from(self.parentWidget().elements)
            self.raise_()

            self.update()

        # Right button press 
        elif event.button() == 2:
            # Trying to add wire ... 
            for contact in self.contacts:
                dx = event.x() - contact.cx
                dy = event.y() - contact.cy

                if dx*dx + dy*dy <= contact.r ** 2:
                    # Coordinates of center of new contact. 
                    new_cx = self.x() + event.x()
                    new_cy = self.y() + event.y()

                    # Connecting to existing wire .. 
                    for link in contact.links:
                        if isinstance(link.element, Wire):
                            link.element.add_segment(
                                link.contact, new_cx, new_cy
                            )
                            self._created_wire = link.element

                            break

                    # or creating new. 
                    else:
                        self._created_wire = self.parentWidget().add_wire(
                            contact.abs_cx, contact.abs_cy, new_cx, new_cy
                        )

                        for link in contact.links:
                            self._created_wire.contacts[0].connect_to(
                                link.contact
                            )
                        self._created_wire.contacts[0].connect_to(contact)

                    break

            # or change switch's condition. 
            else:
                if isinstance(self, Switch):
                    self.condition = not self.condition
                    self.upd()

    def mouseMoveEvent(self, event):
        # Moving self .. 
        if self._press_pos:
            self.move(event.windowPos().toPoint() - self._press_pos)

        # or created_wire's new contact. 
        elif self._created_wire:
            self._created_wire.contacts[-1].move_to(
                self.x() + event.x(), 
                self.y() + event.y()
            )
            self._created_wire.update()

    def mouseReleaseEvent(self, event):
        if self._press_pos:
            self._press_pos = None

            self.connect_to(self.parentWidget().elements)

        elif self._created_wire:
            self._created_wire.connect_to(
                self.parentWidget().elements
            )
            self._created_wire = None

    def enterEvent(self, event):
        self.hover = True
        self.update()

    def leaveEvent(self, event):
        self.hover = False
        self.update()

    # Additional methods 

    def scale(self, q):
        self.scale_value *= q

        width = round(self.default_width * self.scale_value)
        height = round(self.default_height * self.scale_value)

        if self._rotation % 180 == 0:
            self.resize(width, height)
        else:
            self.resize(height, width)

        for contact in self.contacts:
            contact.scale(q)

    def rotate(self, angle):
        self._rotation = (self._rotation + angle) % 360

        if angle % 180 == 0:
            for contact in self.contacts:
                contact.cx = self.width() - contact.cx
                contact.cy = self.height() - contact.cy
        else:
            self.resize(self.height(), self.width())

            for contact in self.contacts:
                if angle > 0:
                    new_cx = self.width() - contact.cy
                    new_cy = contact.cx
                elif angle < 0:
                    new_cx = contact.cy
                    new_cy = self.height() - contact.cx

                contact.cx = new_cx
                contact.cy = new_cy

        self.update()

class And(DraggableElement):
    default_width, default_height, outline, contacts_data = Graphics.And()

    def update_condition(self):
        i0 = self.contacts[0].condition
        i1 = self.contacts[1].condition

        self.contacts[2].condition = i0 and i1

class Or(DraggableElement):
    default_width, default_height, outline, contacts_data = Graphics.Or()

    def update_condition(self):
        i0 = self.contacts[0].condition
        i1 = self.contacts[1].condition

        self.contacts[2].condition = i0 or i1

class Xor(DraggableElement):
    default_width, default_height, outline, contacts_data = Graphics.Xor()

    def update_condition(self):
        i0 = self.contacts[0].condition
        i1 = self.contacts[1].condition

        self.contacts[2].condition = (i0 or i1) and not (i0 and i1)

class Not(DraggableElement):
    default_width, default_height, outline, contacts_data = Graphics.Not()

    def update_condition(self):
        i0 = self.contacts[0].condition

        self.contacts[1].condition = not i0

class Switch(DraggableElement):
    default_width, default_height, base, toggle, toggle_offset, contacts_data = Graphics.Switch()
    condition = False   # False - inactive; True - active 

    def draw_outline(self, painter, pen):
        painter.strokePath(self.base, pen)

        pen.setColor(Palette.switch_toggle.border[self.condition])
        brush = QBrush(Palette.switch_toggle.fill[self.condition])
        painter.setPen(pen)
        painter.setBrush(brush)

        x_offset = self.toggle_offset if self.condition else 0
        painter.translate(x_offset, 0)

        painter.drawPath(self.toggle)

    @classmethod
    def draw_in_panel(cls, painter, panel_width, panel_height):
        # Scaling Switch to stretch it by width of And. 
        scale = And.default_width / cls.default_width

        x_offset = (panel_width - cls.default_width * scale) / 2
        y_offset = (panel_height - cls.default_height * scale) / 2

        painter.translate(x_offset, y_offset)
        painter.scale(scale, scale)

        for data in cls.contacts_data:
            Contact.draw_from_tuple(painter, data)

        painter.drawPath(cls.base)

        painter.setBrush(QBrush(Palette.switch_toggle.fill[False]))
        painter.drawPath(cls.toggle)

    def update_condition(self):
        self.contacts[0].condition = self.condition

class Lamp(DraggableElement):
    default_width, default_height, base, bulb, contacts_data, contact_height = Graphics.Lamp()
    condition = False   # False - inactive; True - active 

    def draw_outline(self, painter, pen):
        painter.setPen(pen)
        painter.drawPath(self.base)

        if self.condition:
            brush = QBrush(Palette.lamp_light)
            painter.setBrush(brush)

        painter.drawPath(self.bulb)

    @classmethod
    def draw_in_panel(cls, painter, panel_width, panel_height):
        height_without_contact = cls.default_height - cls.contact_height

        x_offset = (panel_width - cls.default_width) / 2
        y_offset = (panel_height - height_without_contact) / 2

        painter.translate(x_offset, y_offset)

        painter.drawPath(cls.base)
        painter.drawPath(cls.bulb)

    def update_condition(self):
        self.condition = self.contacts[0].condition

class Wire(LogicElement):
    condition = False

    def __init__(self, parent):
        LogicElement.__init__(self, parent)

        self.contacts = [
            WireContact(self, 0, 0), 
            WireContact(self, 0, 0)
        ]
        self.segments = [WireSegment(self, *self.contacts)]

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        pen = QPen(
            Palette.element.contact[self.condition], 
            round(6 * self.scale_value), 
            Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin
        )
        painter.setPen(pen)

        for wire in self.segments:
            wire.draw(painter)

        for contact in self.contacts:
            contact.draw(painter)

        painter.end()

    def add_segment(self, existing_contact, cx, cy):
        """
        Adds new segment with existing_contact 
        and new contact at cx and cy relative to the window. 
        """

        self.maximize()

        new_contact = WireContact(self, 0, 0)
        new_contact.scale(self.scale_value)
        new_contact.move_to(cx, cy)

        new_segment = WireSegment(self, existing_contact, new_contact)

        self.contacts.append(new_contact)
        self.segments.append(new_segment)

    def scale(self, q):
        self.scale_value *= q

        self.maximize()
        for contact in self.contacts:
            contact.scale(q)
        self.minimize()

    def maximize(self):
        for contact in self.contacts:
            contact.move_to(
                contact.abs_cx + self.x(), 
                contact.abs_cy + self.y()
            )

        self.setGeometry(self.parentWidget().geometry())

    def minimize(self):
        new_geometry = QRect()

        for segment in self.segments:
            new_geometry = new_geometry.united(segment.get_rect())

        new_geometry.adjust(-3, -3, 3, 3)
        # 3 is half of pen width used for drawing wire. 

        for contact in self.contacts:
            contact.move_to(
                contact.abs_cx + (self.x() - new_geometry.x()), 
                contact.abs_cy + (self.y() - new_geometry.y())
            )

        self.setGeometry(new_geometry)

    def join(self, wire):
        pass

    def update_segments(self):
        """
        Determines invalid segments and removes them. 
        """

        while True:
            for segment in self.segments:
                if segment.is_invalid():
                    segment.remove()

                    break
            else:
                break

        if self.segments:
            self.minimize()
            self.upd()
        else:
            self.remove()

    def update_condition(self):
        for contact in self.contacts:
            if contact.condition:
                self.condition = True
                break
        else:
            self.condition = False

        for contact in self.contacts:
            contact.condition = self.condition

class ElementsGroup(QWidget):
    def __init__(self, parent, initial_mouse_pos):
        QWidget.__init__(self, parent)

        self.move(initial_mouse_pos)
        self.resize(0, 0)

        self.elements = set()

        self._initial_mouse_pos = initial_mouse_pos
        self._press_pos = None

        self.setCursor(Qt.PointingHandCursor)
        self.show()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        pen_width = round(2 * self.parentWidget().circuit_scale)

        pen = QPen(
            Palette.elements_group.border, pen_width, 
            Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin
        )
        brush = QBrush(Palette.elements_group.fill)

        painter.setPen(pen)
        painter.setBrush(brush)

        painter.drawRect(
            pen_width, pen_width, 
            self.width() - 2*pen_width, self.height() - 2*pen_width
        )

        painter.end()

    def mousePressEvent(self, event):
        # Only left button press 
        if event.button() == 1:
            self._press_pos = event.pos()

            if self.elements != self.parentWidget().elements:
                for element in self.elements:
                    element.disconnect_from(
                        self.parentWidget().elements - self.elements
                    )
                    element.upd()

            self.setCursor(Qt.SizeAllCursor)

    def mouseMoveEvent(self, event):
        if self._press_pos:
            for element in self.elements:
                element.move(element.pos() + (event.pos() - self._press_pos))

            self.move(self.pos() + (event.pos() - self._press_pos))

    def mouseReleaseEvent(self, event):
        if self._press_pos:
            self._press_pos = None

            if self.elements != self.parentWidget().elements:
                for element in self.elements:
                    element.connect_to(
                        self.parentWidget().elements - self.elements
                    )

            self.update_()
            self.setCursor(Qt.PointingHandCursor)

    def resize_(self, mouse_pos):
        self.setGeometry(
            QRect(self._initial_mouse_pos, mouse_pos).normalized()
        )

    def _align_borders(self):
        new_geometry = QRect()

        for element in self.elements:
            new_geometry = new_geometry.united(element.geometry())

        padding = round(10 * self.parentWidget().circuit_scale)
        new_geometry.adjust(-padding, -padding, padding, padding)

        self.setGeometry(new_geometry)

    def update_(self):
        """
        Removes elements which were removed from sandbox 
        but is still in group. Then checks group validity: 
        it should contain at least 2 elements. 
        """

        self.elements -= self.elements - self.parentWidget().elements

        if len(self.elements) < 2:
            self.parentWidget().remove_elements_group()
        else:
            self._align_borders()
