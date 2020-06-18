"""
Contains widgets used for creating GUI. 
"""

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QPen

from elements import And, Or, Xor, Not, Switch, Lamp, Wire, ElementsGroup
from palette import Palette

class Sandbox(QWidget):
    def __init__(self, parent, initial_scale):
        QWidget.__init__(self, parent)

        self.elements = set()   # Contains all elements of circuit 
        self.circuit_scale = initial_scale

        self._press_pos = None
        self._elements_group = None

        self.show()

    def mousePressEvent(self, event):
        # Left button press 
        if event.button() == 1 and self.elements:
            self.remove_elements_group()
            self.setCursor(Qt.SizeAllCursor)

            self._press_pos = event.pos()

        # Right button press 
        elif event.button() == 2:
            self.create_elements_group(event.pos())

    def mouseMoveEvent(self, event):
        if self._press_pos:
            for element in self.elements:
                element.move(
                    element.pos() + (event.pos() - self._press_pos)
                )
            self._press_pos = event.pos()

        elif self._elements_group:
            self._elements_group.resize_(event.pos())

    def mouseReleaseEvent(self, event):
        if self._elements_group:
            # Adding elements in group 
            for element in self.elements:
                if self._elements_group.geometry().contains(element.geometry()):
                    self._elements_group.elements.add(element)

            self._elements_group.update_()

        self._press_pos = None
        self.setCursor(Qt.ArrowCursor)

    def add_element(self, element_constructor, mouse_pos):
        new_element = element_constructor(self)

        new_element.scale(self.circuit_scale)
        new_element.move(
            mouse_pos - new_element.geometry().center()
        )

        # When element is created it already hovered. 
        new_element.hover = True

        self.elements.add(new_element)

        return new_element

    def remove_element(self, element):
        element.disconnect_from(self.elements)
        element.close()

        if element in self.elements:
            self.elements.remove(element)

    def add_wire(self, *contacts_coords):
        new_wire = Wire(self)

        new_wire.lower()
        self.window().toolbar.stackUnder(new_wire)

        new_wire.scale(self.circuit_scale)
        new_wire.maximize()

        new_wire.contacts[0].move_to(*contacts_coords[:2])
        new_wire.contacts[1].move_to(*contacts_coords[2:])

        self.elements.add(new_wire)

        return new_wire

    def create_elements_group(self, mouse_pos):
        self.remove_elements_group()
        self._elements_group = ElementsGroup(self, mouse_pos)

        self.setCursor(Qt.CrossCursor)

    def remove_elements_group(self, remove_elements=False):
        if self._elements_group:
            if remove_elements:
                for element in self._elements_group.elements:
                    self.remove_element(element)

            self._elements_group.close()
            self._elements_group = None

    def clear(self):
        for element in self.elements:
            element.close()
        self.elements.clear()

        self.remove_elements_group()
        self._press_pos = None

        self.setCursor(Qt.ArrowCursor)

class Toolbar(QWidget):
    def __init__(self, parent, height):
        QWidget.__init__(self, parent)

        spacing = round(height * 0.125)
        panel_height = height - 2*spacing
        panel_width = round(
            panel_height / ElementPanel.default_height * ElementPanel.default_width
        )

        elements = And, Or, Xor, Not, Switch, Lamp

        for n in range(len(elements)):
            new_panel = ElementPanel(self, elements[n])
            new_panel.move(spacing + n *(panel_width + spacing), spacing)
            new_panel.resize(panel_width, panel_height)

        self.resize(
            len(elements) * (panel_width + spacing) + spacing, height
        )
        self.show()

class ElementPanel(QWidget):
    default_width = 420
    default_height = 250

    def __init__(self, parent, element_constructor):
        QWidget.__init__(self, parent)

        self._element_constructor = element_constructor

        # When new element was created but panel hasn't released yet, 
        # created_element stores this element. 
        self._created_element = None

        self.setCursor(Qt.PointingHandCursor)
        self.show()

    def mousePressEvent(self, event):
        # Only left button press 
        if event.button() == 1:
            sandbox = self.window().sandbox

            self._created_element = sandbox.add_element(
                self._element_constructor, event.windowPos().toPoint()
            )
            sandbox.remove_elements_group()

    def mouseMoveEvent(self, event):
        if self._created_element:
            new_geometry = self._created_element.geometry()
            new_geometry.moveCenter(event.windowPos().toPoint())

            self._created_element.setGeometry(new_geometry)

    def mouseReleaseEvent(self, event):
        if self._created_element:
            self._created_element.connect_to(
                self.window().sandbox.elements
            )
            self._created_element = None

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        x_scale = self.width() / self.default_width
        y_scale = self.height() / self.default_height

        painter.scale(x_scale, y_scale)

        # Drawing border 

        pen = QPen(
            Palette.panel_border, 10, 
            Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin
        )
        painter.setPen(pen)

        painter.drawRoundedRect(
            5, 5, 
            self.default_width - 10, self.default_height - 10, 
            40, 40
        )

        # Drawing element 

        pen.setWidth(6)
        painter.setPen(pen)

        self._element_constructor.draw_in_panel(
            painter, self.default_width, self.default_height
        )

        painter.end()
