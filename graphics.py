from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainterPath


class Graphics:
    """
    Contains graphic information about each circuit element such as: 
    - width and height; 
    - outline: part of element distinguishing it from others; 
    - contacts data: tuples of arguments passing to class Contact 
      when initialize its instance; 
    """

    __new__ = None

    __And = None
    __Or = None
    __Xor = None
    __Not = None
    __Switch = None
    __Lamp = None

    @classmethod
    def And(cls):
        if cls.__And is None:
            width = 380
            height = 200

            outline = QPainterPath()
            outline.moveTo(81, 3)
            outline.cubicTo(371, -5, 371, 205, 81, 197)
            outline.closeSubpath()

            contacts_data = (
                ("i", 13, 50, cls.__create_wire(23, 50, 81, 50)),
                ("i", 13, 150, cls.__create_wire(23, 150, 81, 150)),
                ("o", 367, 100, cls.__create_wire(299, 100, 357, 100))
            )

            cls.__And = (width, height, outline, contacts_data)

        return cls.__And

    @classmethod
    def Or(cls):
        if cls.__Or is None:
            width = 380
            height = 200

            outline = QPainterPath()
            outline.moveTo(81, 3)
            outline.cubicTo(371, 23, 371, 177, 81, 197)
            outline.quadTo(145, 100, 81, 3)
            outline.closeSubpath()

            contacts_data = (
                ("i", 13, 50, cls.__create_wire(23, 50, 104, 50)),
                ("i", 13, 150, cls.__create_wire(23, 150, 104, 150)),
                ("o", 367, 100, cls.__create_wire(299, 100, 357, 100))
            )

            cls.__Or = (width, height, outline, contacts_data)

        return cls.__Or

    @classmethod
    def Xor(cls):
        if cls.__Xor is None:
            width = 380
            height = 200

            outline = QPainterPath()
            outline.moveTo(81, 3)
            outline.cubicTo(371, 23, 371, 177, 81, 197)
            outline.quadTo(145, 100, 81, 3)
            outline.closeSubpath()
            outline.moveTo(66, 3)
            outline.quadTo(130, 100, 66, 197)

            contacts_data = (
                ("i", 13, 50, cls.__create_wire(23, 50, 89, 50)),
                ("i", 13, 150, cls.__create_wire(23, 150, 89, 150)),
                ("o", 367, 100, cls.__create_wire(299, 100, 357, 100))
            )

            cls.__Xor = (width, height, outline, contacts_data)

        return cls.__Xor

    @classmethod
    def Not(cls):
        if cls.__Not is None:
            width = 340
            height = 200

            outline = QPainterPath()
            outline.moveTo(242, 95)
            outline.lineTo(82, 3)
            outline.lineTo(82, 197)
            outline.lineTo(242, 105)
            outline.addEllipse(242, 90, 20, 20)

            contacts_data = (
                ("i", 13, 100, cls.__create_wire(23, 100, 81, 100)),
                ("o", 327, 100, cls.__create_wire(262, 100, 317, 100))
            )

            cls.__Not = (width, height, outline, contacts_data)

        return cls.__Not

    @classmethod
    def Switch(cls):
        if cls.__Switch is None:
            width = 250
            height = 100

            # base 

            base = QPainterPath()
            base.addRoundedRect(3, 3, 178, 94, 47, 47)

            # toggle 

            toggle = QPainterPath()
            toggle.addEllipse(13, 13, 74, 74)

            toggle_offset = 84

            contacts_data = (
                ("o", 237, 50, cls.__create_wire(181, 50, 227, 50)),
            )

            cls.__Switch = (width, height, base, toggle, toggle_offset, contacts_data)

        return cls.__Switch

    @classmethod
    def Lamp(cls):
        if cls.__Lamp is None:
            width = 140
            height = 250

            # base 

            base = QPainterPath()
            base.moveTo(103, 196)
            base.lineTo(37, 196)
            base.moveTo(52, 197)
            base.arcTo(51, 173, 38, 38, -165, 150)

            # bulb 

            bulb = QPainterPath()
            bulb.moveTo(35, 188)
            bulb.lineTo(32, 185)
            bulb.quadTo(34, 138, 15, 108)
            bulb.arcTo(3, 3, 134, 134, -157, -235)
            bulb.quadTo(106, 138, 108, 185)
            bulb.lineTo(105, 188)
            bulb.closeSubpath()
            bulb.moveTo(58, 187)
            bulb.lineTo(50, 118)
            bulb.lineTo(90, 118)
            bulb.lineTo(82, 187)
            bulb.setFillRule(Qt.WindingFill)

            contacts_data = (
                ("i", 70, 237, cls.__create_wire(70, 227, 70, 211)),
            )

            cls.__Lamp = (width, height, base, bulb, contacts_data)

        return cls.__Lamp

    @staticmethod
    def __create_wire(x0, y0, x1, y1):
        wire = QPainterPath()
        wire.moveTo(x0, y0)
        wire.lineTo(x1, y1)

        return wire
