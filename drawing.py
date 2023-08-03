
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *


class DrawingArea:
    class ExtraDrawingArea(Exception): pass

    def __init__(self):
        if DrawingArea._is_instance:
            raise DrawingArea.ExtraDrawingArea
        self._is_instance = True

        self.scene = QGraphicsScene()
        black_brush = QBrush()
        black_brush.setColor(QColorConstants.Black)
        self.scene.addRect(50, 50, 150, 150, brush=black_brush)

    _is_instance = False
