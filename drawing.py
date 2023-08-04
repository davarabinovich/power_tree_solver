import sys

from PyQt6.QtWidgets import *
from PyQt6.QtGui import *


class DrawingArea:
    class ExtraDrawingArea(Exception): pass

    def __init__(self):
        if DrawingArea._is_instance:
            raise DrawingArea.ExtraDrawingArea
        self._is_instance = True
        self._scene = QGraphicsScene()
        self.add_node()

    def add_node(self):
        rect = GraphNode(50, 100)
        self._scene.addItem(rect)
        rect.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)

    @property
    def scene(self):
        return self._scene
    @scene.setter
    def scene(self, value):
        self._scene = value

    _is_instance = False


class GraphNode(QGraphicsRectItem):
    WIDTH = 100
    HEIGHT = 50

    def __init__(self, x, y):
        super().__init__(x, y, self.WIDTH, self.HEIGHT)
        pen = QPen(QColorConstants.Yellow, 5)
        brush = QBrush(QColorConstants.Black)
        super().setPen(pen)
        super().setBrush(brush)

    def mousePressEvent(self, *args, **kwargs):
        sys.exit()
