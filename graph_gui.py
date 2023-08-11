
from __future__ import annotations

import sys
import typing
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *


# TODO: Try to separate scene from view creating another class GraphGUI referencing both them
class GraphView(QGraphicsView):
    class ExtraDrawingArea(Exception): pass

    def __init__(self, parent: QWidget=None):
        if GraphView._is_instance:
            raise GraphView.ExtraDrawingArea
        self._is_instance = True

        super().__init__(parent)
        self._scene = GraphScene()
        self.setScene(self._scene)

        self._root_insertion_y = 100
        self.add_root()

    def add_root(self):
        rect = GraphNode()
        rect.new_child_called.connect(self.add_child)
        self._scene.addItem(rect)
        x, y = self._calc_new_root_coords()
        rect.moveBy(x, y)

    def add_child(self):
        sys.exit()

    def _calc_new_root_coords(self):
        x = GraphView._X
        y = self._root_insertion_y
        self._root_insertion_y += 2 * GraphNode.HEIGHT
        return x, y

    _X = 50

    _is_instance = False


class GraphScene(QGraphicsScene):
    def __init__(self):
        super().__init__()


class GraphNode(QGraphicsObject):
    WIDTH = 100
    HEIGHT = 50
    ROUNDING = 5

    FILLING_COLOR = QColorConstants.Black
    OUTLINE_COLOR = QColorConstants.Yellow
    OUTLINE_THICKNESS = 5

    CROSS_GAP = 5

    def __init__(self):
        super().__init__(None)
        cross = CrossIcon(self)
        cross.clicked.connect(self.new_child_called)
        cross.moveBy(GraphNode.WIDTH+GraphNode.CROSS_GAP, 0)

    def boundingRect(self) -> QRectF:
        xl = -GraphNode.OUTLINE_THICKNESS / 2
        yt = -GraphNode.OUTLINE_THICKNESS / 2
        delta_x = GraphNode.WIDTH + GraphNode.CROSS_GAP + CrossIcon.DIAMETER
        delta_y = GraphNode.HEIGHT + GraphNode.OUTLINE_THICKNESS
        rect = QRectF(xl, yt, delta_x, delta_y)
        return rect

    def paint(self, painter: QPainter=None, *args, **kwargs):
        pen = QPen(GraphNode.OUTLINE_COLOR, GraphNode.OUTLINE_THICKNESS)
        brush = QBrush(GraphNode.FILLING_COLOR)
        painter.setPen(pen)
        painter.setBrush(brush)
        painter.drawRoundedRect(0, 0, GraphNode.WIDTH, GraphNode.HEIGHT, GraphNode.ROUNDING, GraphNode.ROUNDING)

    new_child_called = pyqtSignal()


class CrossIcon(QGraphicsWidget):
    DIAMETER = 12
    LINE_LENGTH = 8

    CIRCLE_COLOR = QColorConstants.Green
    LINE_COLOR = QColorConstants.White
    LINE_THICKNESS = 3

    LINE_GAP = (DIAMETER - LINE_LENGTH) / 2
    RADIUS = DIAMETER / 2

    def __init__(self, parent: QGraphicsItem=None):
        super().__init__(parent)

    def boundingRect(self) -> QRectF:
        rect = QRectF(0, 0, CrossIcon.DIAMETER, CrossIcon.DIAMETER)
        return rect

    def paint(self, painter: QPainter=None, *args, **kwargs):
        pen = QPen(CrossIcon.CIRCLE_COLOR, 0)
        brush = QBrush(CrossIcon.CIRCLE_COLOR)
        painter.setPen(pen)
        painter.setBrush(brush)
        painter.drawEllipse(0, 0, CrossIcon.DIAMETER, CrossIcon.DIAMETER)

        pen = QPen(CrossIcon.LINE_COLOR, CrossIcon.LINE_THICKNESS)
        painter.setPen(pen)
        top_point = QPointF(CrossIcon.RADIUS, CrossIcon.LINE_GAP)
        bottom_point = QPointF(CrossIcon.RADIUS, CrossIcon.DIAMETER-CrossIcon.LINE_GAP)
        painter.drawLine(top_point, bottom_point)

        left_point = QPointF(CrossIcon.LINE_GAP, CrossIcon.RADIUS)
        right_point = QPointF(CrossIcon.DIAMETER-CrossIcon.LINE_GAP, CrossIcon.RADIUS)
        painter.drawLine(left_point, right_point)

    def mousePressEvent(self, event, QGraphicsSceneMouseEvent=None):
        self.clicked.emit()

    clicked = pyqtSignal()
