# Contains logic elements widgets for creating circuits. 

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QCursor, QPainter, QPen, QBrush

from connections import Contact

from graphics import Graphics
from palette import Palette

class LogicElement(QWidget):
    def __init__(self, parent):
        QWidget.__init__(self, parent)

        self.contacts = []
        for data in self.contacts_data:
            self.contacts.append(Contact(self, *data))

        self.scale_value = 1
        
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

    def connect_to_others(self):
        self.upd()
        for element in self.parentWidget().elements:
            if element is not self:
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

    def clear_links(self):
        for contact in self.contacts:
            contact.clear_links()

            contact.condition = False

        if isinstance(self, (Switch, Lamp)):
            self.update_condition()

class DraggableElement(LogicElement):
    def __init__(self, parent):
        LogicElement.__init__(self, parent)

        self.press_pos = None
        self.hover = True   # When element is created it already hovered. 

        self.setCursor(Qt.PointingHandCursor)

    def mousePressEvent(self, event):
        # Left button press 
        if event.button() == 1:
            self.press_pos = event.pos()
            self.clear_links()
            self.update()
        # Right button press 
        elif event.button() == 2:
            if isinstance(self, Switch):
                self.condition = not self.condition
                self.upd()

    def mouseMoveEvent(self, event):
        if self.press_pos:
            self.move(event.windowPos().toPoint() - self.press_pos)

    def mouseReleaseEvent(self, event):
        if self.press_pos:
            self.press_pos = None
            self.raise_()

            self.connect_to_others()

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
