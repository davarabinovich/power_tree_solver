
import sys

from PyQt6.QtWidgets import *
from PyQt6.QtGui import *


class DrawingArea:
    class ExtraDrawingArea(Exception): pass

    def __init__(self, graphics_view: QGraphicsView):
        if DrawingArea._is_instance:
            raise DrawingArea.ExtraDrawingArea
        self._is_instance = True

        self._scene = GraphScene()
        self._view = graphics_view
        self._view.setScene(self._scene)

        self._context_menu = QMenu(self._view)
        create_node_action = self._context_menu.addAction("Create New Node")
        create_node_action.triggered.connect(self.add_node)

        self.add_node()

    def add_node(self):
        rect = GraphNode(50, 100)
        self._scene.addItem(rect)

    @property
    def scene(self):
        return self._scene
    @scene.setter
    def scene(self, value):
        self._scene = value

    _is_instance = False


class GraphScene(QGraphicsScene):
    def __init__(self):
        super().__init__()

    def contextMenuEvent(self, *args, **kwargs):
        pass


class GraphNode(QGraphicsRectItem):
    WIDTH = 100
    HEIGHT = 50

    def __init__(self, x, y):
        super().__init__(x, y, self.WIDTH, self.HEIGHT)
        pen = QPen(QColorConstants.Yellow, 5)
        brush = QBrush(QColorConstants.Black)
        super().setPen(pen)
        super().setBrush(brush)

        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)

    def mousePressEvent(self, *args, **kwargs):
        sys.exit()
