# Contains widgets used for creating GUI. 

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QPen

from elements import And, Or, Xor, Not, Switch, Lamp, ElementsGroup
from palette import Palette

class Sandbox(QWidget):
    def __init__(self, parent, initial_scale):
        QWidget.__init__(self, parent)

        self.elements = []   # Contains all elements of circuit 
        self.circuit_scale = initial_scale

        self.press_pos = None
        self.elements_group = None

        self.show()

    def mousePressEvent(self, event):
        # Left button press 
        if event.button() == 1 and self.elements:
            self.remove_elements_group()
            self.setCursor(Qt.SizeAllCursor)

            self.press_pos = event.pos()

        # Right button press 
        elif event.button() == 2:
            self.create_elements_group(event.pos())

    def mouseMoveEvent(self, event):
        if self.press_pos:
            for element in self.elements:
                element.move(
                    element.pos() + (event.pos() - self.press_pos)
                )
            self.press_pos = event.pos()

        elif self.elements_group:
            self.elements_group.resize_(event.x(), event.y())

    def mouseReleaseEvent(self, event):
        if self.elements_group:
            # Adding elements in group 
            for element in self.elements:
                if self.elements_group.geometry().contains(element.geometry()):
                    self.elements_group.elements.append(element)

            # Checking group validity: 
            # it should contain at least 2 elements. 

            if len(self.elements_group.elements) < 2:
                self.remove_elements_group()
            else:
                self.elements_group.align_borders()

        self.press_pos = None
        self.setCursor(Qt.ArrowCursor)

    def add_element(self, element_constructor, window_x, window_y):
        new_element = element_constructor(self)

        new_element.scale(self.circuit_scale)
        new_element.move(window_x - new_element.width() / 2,
                         window_y - new_element.height() / 2)

        self.elements.append(new_element)

        return new_element

    def remove_element(self, element):
        element.clear_links()
        element.close()

        self.elements.remove(element)

    def create_elements_group(self, window_pos):
        self.remove_elements_group()
        self.elements_group = ElementsGroup(self, window_pos)

        self.setCursor(Qt.CrossCursor)

    def remove_elements_group(self, remove_elements=False):
        if self.elements_group:
            if remove_elements:
                for element in self.elements_group.elements:
                    self.remove_element(element)

            self.elements_group.close()
            self.elements_group = None

    def clear(self):
        for element in self.elements:
            element.close()
        self.elements.clear()

        self.remove_elements_group()
        self.press_pos = None

        self.setCursor(Qt.ArrowCursor)

class Toolbar(QWidget):
    def __init__(self, parent, height):
        QWidget.__init__(self, parent)

        spacing = round(height * 0.125)
        panel_height = height - 2*spacing
        panel_width = round(panel_height / ElementPanel.default_height * ElementPanel.default_width)

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

        self.element_constructor = element_constructor

        # When new element was created but panel hasn't released yet, 
        # created_element stores this element. 
        self.created_element = None

        self.setCursor(Qt.PointingHandCursor)
        self.show()

    def mousePressEvent(self, event):
        # Only left button press 
        if event.button() == 1:
            sandbox = self.window().sandbox
            window_pos = event.windowPos()

            self.created_element = sandbox.add_element(
                self.element_constructor, 
                window_pos.x(), window_pos.y()
            )
            sandbox.remove_elements_group()

    def mouseMoveEvent(self, event):
        if self.created_element:
            window_pos = event.windowPos()

            self.created_element.move(
                window_pos.x() - self.created_element.width() / 2, 
                window_pos.y() - self.created_element.height() / 2
            )

    def mouseReleaseEvent(self, event):
        if self.created_element:
            self.created_element.connect_to_others()
            self.created_element = None

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
            5, 5, self.default_width - 10, self.default_height - 10, 40, 40
        )

        # Drawing element 

        pen.setWidth(6)
        painter.setPen(pen)

        self.element_constructor.draw_in_panel(
            painter, self.default_width, self.default_height
        )

        painter.end()
