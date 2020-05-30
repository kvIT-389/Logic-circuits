# Contains logic elements widgets for creating circuits. 

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QPen, QBrush

from connections import Contact, WireContact, WireSegment

from graphics import Graphics
from palette import Palette

class LogicElement(QWidget):
    default_width = 0
    default_height = 0

    def __init__(self, parent):
        QWidget.__init__(self, parent)

        try:
            self.contacts = []
            for data in self.contacts_data:
                self.contacts.append(Contact(self, *data))
        except AttributeError:
            pass

        self.scale_value = 1
        self.hover = False

        self.resize(self.default_width, self.default_height)
        self.show()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        painter.scale(self.scale_value, self.scale_value)

        if self.hover:
            pen = QPen(
                Palette.element.border, 2.5, 
                Qt.DotLine, Qt.RoundCap, Qt.RoundJoin
            )

            painter.setPen(pen)
            painter.drawRect(
                2, 2, self.default_width - 4, self.default_height - 4
            )

        for contact in self.contacts:
            contact.draw(painter)

        pen = QPen(
            Palette.element.outline, 6, 
            Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin
        )
        self.draw_outline(painter, pen)

        painter.end()

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

    def scale(self, q):
        self.scale_value *= q

        width = self.default_width * self.scale_value
        height = self.default_height * self.scale_value

        self.resize(width, height)

        for contact in self.contacts:
            contact.scale(q)

    def connect_to_others(self, connected_elements=[]):
        self.upd()
        for element in self.parentWidget().elements:
            if (element is not self) and (element not in connected_elements):
                for contact_0 in self.contacts:
                    for contact_1 in element.contacts:
                        contact_0.try_to_connect_to(contact_1)

    def upd(self):
        for contact in self.contacts:
            contact.receive_signals()

        self.update_condition()

        for contact in self.contacts:
            contact.transmit_signal()

        self.update()

    def clear_links(self, unaffected_elements=[]):
        # unaffected_elements contains elements 
        # which shouldn't be disconnected. 

        for contact in self.contacts:
            contact.clear_links(unaffected_elements)

            contact.condition = False

        if isinstance(self, (Switch, Lamp)):
            self.update_condition()

class DraggableElement(LogicElement):
    def __init__(self, parent):
        LogicElement.__init__(self, parent)

        self.press_pos = None

        # At the time of creation of new wire (or its new segment), 
        # created_wire stores this new (or already existing) wire. 
        self.created_wire = None

        self.setCursor(Qt.PointingHandCursor)

    def mousePressEvent(self, event):
        # Left button press 
        if event.button() == 1:
            self.press_pos = event.pos()

            self.clear_links()
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
                            link.element.add_segment(link.contact, 
                                                     new_cx, new_cy)
                            self.created_wire = link.element

                            break

                    # or creating new. 
                    else:
                        self.created_wire = self.parentWidget().add_wire(
                            contact.abs_cx, contact.abs_cy, new_cx, new_cy
                        )

                        for link in contact.links:
                            self.created_wire.contacts[0].connect_to(
                                link.contact
                            )
                        self.created_wire.contacts[0].connect_to(contact)

                    break

            # or change switch's condition. 
            else:
                if isinstance(self, Switch):
                    self.condition = not self.condition
                    self.upd()

    def mouseMoveEvent(self, event):
        # Moving self .. 
        if self.press_pos:
            self.move(event.windowPos().toPoint() - self.press_pos)

        # or created_wire's new contact. 
        elif self.created_wire:
            self.created_wire.contacts[-1].move_to(
                self.x() + event.x(), 
                self.y() + event.y()
            )
            self.created_wire.update()

    def mouseReleaseEvent(self, event):
        if self.press_pos:
            self.press_pos = None

            self.connect_to_others()

        elif self.created_wire:
            self.created_wire.end_creating()
            self.created_wire = None

    def enterEvent(self, event):
        self.hover = True
        self.update()

    def leaveEvent(self, event):
        self.hover = False
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

    def add_segment(self, existing_contact, new_cx, new_cy):
        self.maximize()

        new_contact = WireContact(self, 0, 0)
        new_contact.scale(self.scale_value)
        new_contact.move_to(new_cx, new_cy)

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
            contact.move_to(contact.abs_cx, contact.abs_cy)

        self.setGeometry(self.parentWidget().geometry())

    def minimize(self):
        cxs = []
        cys = []

        for contact in self.contacts:
            cxs.append(contact.cx)
            cys.append(contact.cy)

        r = self.contacts[0].r + 3
        # 3 is half of pen width used for drawing wire. 

        x = min(cxs) - r
        y = min(cys) - r
        w = max(cxs) - x + r
        h = max(cys) - y + r

        self.setGeometry(x, y, w, h)

        for contact in self.contacts:
            contact.move_to(contact.cx - x, contact.cy - y)

    def end_creating(self):
        # Ends creating wire or its new segment. 

        self.upd()

        for element in self.parentWidget().elements:
            if element is not self:
                for contact in element.contacts:
                    self.contacts[-1].try_to_connect_to(contact)

        self.minimize()

    def update_condition(self):
        pass

class ElementsGroup(QWidget):
    def __init__(self, parent, initial_mouse_pos):
        QWidget.__init__(self, parent)

        self.move(initial_mouse_pos)
        self.resize(0, 0)

        self.initial_mouse_x = initial_mouse_pos.x()
        self.initial_mouse_y = initial_mouse_pos.y()

        self.elements = []

        self.press_pos = None

        self.setCursor(Qt.PointingHandCursor)
        self.show()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        pen_width = round(2 * self.parentWidget().circuit_scale)

        pen = QPen(
            Palette.group.border, pen_width, 
            Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin
        )
        brush = QBrush(Palette.group.fill)

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
            self.press_pos = event.pos()

            if self.elements != self.parentWidget().elements:
                for element in self.elements:
                    element.clear_links(self.elements)
                    element.upd()

            self.setCursor(Qt.SizeAllCursor)

    def mouseMoveEvent(self, event):
        for element in self.elements:
            element.move(element.pos() + (event.pos() - self.press_pos))

        self.move(self.pos() + (event.pos() - self.press_pos))

    def mouseReleaseEvent(self, event):
        if self.press_pos:
            self.press_pos = None

            if self.elements != self.parentWidget().elements:
                for element in self.elements:
                    element.connect_to_others(self.elements)

            self.setCursor(Qt.PointingHandCursor)

    def resize_(self, mouse_x, mouse_y):
        self.setGeometry(min(self.initial_mouse_x, mouse_x), 
                         min(self.initial_mouse_y, mouse_y), 
                         abs(mouse_x - self.initial_mouse_x), 
                         abs(mouse_y - self.initial_mouse_y)
        )

    def align_borders(self):
        left_borders = []
        top_borders = []
        right_borders = []
        bottom_borders = []

        for element in self.elements:
            left_borders.append(element.x())
            top_borders.append(element.y())
            right_borders.append(element.x() + element.width())
            bottom_borders.append(element.y() + element.height())

        padding = round(8 * self.parentWidget().circuit_scale)

        x = min(left_borders) - padding
        y = min(top_borders) - padding
        w = max(right_borders) - x + 2*padding
        h = max(bottom_borders) - y + 2*padding

        self.setGeometry(x, y, w, h)
