# Contains all colors using in application. 

from PyQt5.QtGui import QColor

class Palette:
    panel_border = QColor(62, 63, 65)

    class element:
        border = QColor(159, 167, 158)
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

    __new__ = None
