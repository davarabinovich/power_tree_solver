import sys

from PyQt6.QtWidgets import *
from PyQt6.QtGui import *


class DrawingArea:
    class ExtraDrawingArea(Exception): pass

    def __init__(self):
        if DrawingArea._is_instance:
            raise DrawingArea.ExtraDrawingArea
        self._is_instance = True

        self.scene = QGraphicsScene()

        yellow_pen = QPen(QColorConstants.Yellow)
        yellow_pen.setWidth(5)
        black_brush = QBrush(QColorConstants.Black)
        rect = MyRect(50, 50, 150, 150)
        rect.setPen(yellow_pen)
        rect.setBrush(black_brush)
        self.scene.addItem(rect)
        rect.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)

    _is_instance = False


class MyRect(QGraphicsRectItem):
    def __init__(self, *argv):
        super().__init__(*argv)

    def mousePressEvent(self, *args, **kwargs):
        sys.exit()
