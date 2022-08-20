"""
Contains widgets used for creating GUI. 
"""

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel
from PyQt5.QtGui import QPainter, QPixmap

from elements import And, Or, Xor, Not, Switch, Lamp, Wire, ElementsGroup


class Sandbox(QWidget):
    def __init__(self, parent, initial_scale):
        QWidget.__init__(self, parent)

        self.elements = set()
        self.circuit_scale = initial_scale

        self._press_pos = None
        self._elements_group = None

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

    def add_element(self, element_constructor):
        new_element = element_constructor(self)
        new_element.scale(self.circuit_scale)

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

        spacing = height * 0.125
        panel_height = height - 2*spacing

        self.setLayout(QHBoxLayout())

        self.layout().setSpacing(spacing)
        self.layout().setContentsMargins(*(spacing,) * 4)
        self.layout().setAlignment(Qt.AlignLeft)

        elements = And, Or, Xor, Not, Switch, Lamp
        for element in elements:
            new_panel = ElementPanel(panel_height, element)
            self.layout().addWidget(new_panel)

        self.resize(0, height)


class ElementPanel(QLabel):
    def __init__(self, height, element_constructor):
        QLabel.__init__(self, "")

        self._element_constructor = element_constructor

        # When new element was created but panel hasn't released yet, 
        # _created_element stores this element. 
        self._created_element = None

        self._border = QPixmap("png/Border.png").scaledToHeight(
            height, Qt.SmoothTransformation
        )
        self.setFixedSize(self._border.size())

        self._update_icon()

        self.setCursor(Qt.PointingHandCursor)

    def _update_icon(self):
        self._icon = QPixmap(
            f"png/{self._element_constructor.__name__}.png"
        ).scaled(
            self.width() * 0.88, self.height() * 0.83,
            Qt.KeepAspectRatio, Qt.SmoothTransformation
        )

    def mousePressEvent(self, event):
        # Only left button press 
        if event.button() == 1:
            sandbox = self.window().sandbox

            self._created_element = sandbox.add_element(
                self._element_constructor
            )

            self._created_element.move(
                event.windowPos().toPoint() -
                self._created_element.geometry().center()
            )

            # When element was created, it already hovered. 
            self._created_element.hover = True

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

        painter.drawPixmap(0, 0, self._border)
        painter.drawPixmap(
            (self.width() - self._icon.width()) * 0.5,
            (self.height() - self._icon.height()) * 0.5,
            self._icon
        )

        painter.end()
