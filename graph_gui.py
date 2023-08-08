
from __future__ import annotations
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *


class GraphView(QGraphicsView):
    class ExtraDrawingArea(Exception): pass

    def __init__(self, parent=None):
        if GraphView._is_instance:
            raise GraphView.ExtraDrawingArea
        self._is_instance = True

        super().__init__(parent)
        self._scene = QGraphicsScene()
        self.setScene(self._scene)

        self._context_menu = QMenu(self)
        create_node_action = self._context_menu.addAction("Create New Node")
        create_node_action.triggered.connect(self.add_root)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.handle_context_menu_call)

        self._y = 100
        self.add_root()

    def handle_context_menu_call(self, local_pos):
        global_pos = self.mapToGlobal(local_pos)
        self._context_menu.exec(global_pos)

    def add_root(self):
        x, y = self._calc_new_node_coords()
        rect = GraphNode(x, y)
        self._scene.addItem(rect)

    def add_child(self, node: GraphNode):
        pass

    def _calc_new_node_coords(self):
        x = GraphView._X
        y = self._y
        self._y += 2 * GraphNode.HEIGHT
        return x, y

    _X = 50

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

        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
