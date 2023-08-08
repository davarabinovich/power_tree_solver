
from __future__ import annotations
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *


class DrawingArea():
    class ExtraDrawingArea(Exception): pass

    def __init__(self, view: GraphView):
        if DrawingArea._is_instance:
            raise DrawingArea.ExtraDrawingArea
        self._is_instance = True

        self._scene = QGraphicsScene()
        self._view = view
        self._view.initialize(self)
        self._view.setScene(self._scene)

        self._y = 100
        self.add_root()

    def add_root(self):
        x, y = self._calc_new_node_coords()
        rect = GraphNode(x, y, self.add_child)
        self._scene.addItem(rect)

    def add_child(self, node: GraphNode):
        pass

    @property
    def scene(self):
        return self._scene
    @scene.setter
    def scene(self, value):
        self._scene = value

    def _calc_new_node_coords(self):
        x = DrawingArea._X
        y = self._y
        self._y += 2 * GraphNode.HEIGHT
        return x, y

    _X = 50

    _is_instance = False


class GraphView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._area = None
        self._context_menu = QMenu(self)

    def initialize(self, area: DrawingArea):
        self._area = area
        create_node_action = self._context_menu.addAction("Create New Node")
        create_node_action.triggered.connect(self._area.add_root)

    def contextMenuEvent(self, event):
        self._context_menu.exec(event.globalPos())


class GraphNode(QGraphicsRectItem, QWidget):
    WIDTH = 100
    HEIGHT = 50

    def __init__(self, x, y, add_child_func):
        super().__init__(x, y, self.WIDTH, self.HEIGHT)
        pen = QPen(QColorConstants.Yellow, 5)
        brush = QBrush(QColorConstants.Black)
        super().setPen(pen)
        super().setBrush(brush)

        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)

        self._context_menu = QMenu(self)
        create_child_action = self._context_menu.addAction("Create Child Node")
        create_child_action.triggered.connect(add_child_func)

    def contextMenuEvent(self, event):
        self._context_menu.exec(event.globalPos())
