from PyQt5.QtGui import QColor

class Palette:
    """
    Contains all colors using in application. 
    """

    __new__ = None

    panel_border = QColor(62, 63, 65)

    class elements_group:
        border = QColor(128, 132, 129)
        fill = QColor(200, 200, 200, 20)

    class element:
        border = QColor(189, 187, 188)
        outline = QColor(73, 74, 76)

        contact = {
            False: QColor(73, 74, 76),   # inactive contact 
            True: QColor(162, 73, 71)    # active contact 
        }

    class switch_toggle:
        border = {
            False: QColor(68, 69, 67),   # inactive switch 
            True: QColor(103, 14, 12)    # active switch 
        }
        fill = {
            False: QColor(102, 103, 105),   # inactive switch 
            True: QColor(167, 78, 76)       # active switch 
        }

    lamp_light = QColor(210, 207, 24, 200)
