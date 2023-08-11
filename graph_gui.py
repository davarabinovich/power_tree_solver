
from __future__ import annotations

import sys
import typing
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *


# TODO: Try to separate scene from view creating another class GraphGUI referencing both them
class GraphView(QGraphicsView):
    HORIZONTAL_GAP = 50
    VERTICAL_GAP = 50
    CROSS_X = 20
    CROSS_Y = 200

    CONNECTION_LINE_COLOR = QColorConstants.Red
    CONNECTION_LINE_THICKNESS = 3

    class ExtraDrawingArea(Exception): pass

    def __init__(self, parent: QWidget=None):
        if GraphView._is_instance:
            raise GraphView.ExtraDrawingArea
        self._is_instance = True

        super().__init__(parent)
        self._nodes = []
        self._scene = QGraphicsScene()
        self.setScene(self._scene)

        cross = CrossIcon()
        self._scene.addItem(cross)
        cross.moveBy(GraphView.CROSS_X, GraphView.CROSS_Y)
        cross.clicked.connect(self.add_root)

        self._root_insertion_y = 100
        self.add_root()

    @pyqtSlot()
    def add_root(self):
        x, y = self._calc_new_root_coords()
        self._add_node(x,y)

    # TODO: replace QGraphicsItem with GraphNode
    @pyqtSlot(QGraphicsItem)
    def add_child(self, parent: QGraphicsItem):
        x, y = GraphView._calc_new_child_coords(parent)
        child = self._add_node(x, y)
        parent_children_number = parent.data(GraphView._ITEM_DATA_KEYS_DICT["children_number"])
        parent.setData(GraphView._ITEM_DATA_KEYS_DICT["children_number"], parent_children_number+1)
        self._draw_connection_line(parent, child)

    def _add_node(self, x, y):
        node = GraphNode()
        node.setData(GraphView._ITEM_DATA_KEYS_DICT["children_number"], 0)
        node.newChildCalled.connect(self.add_child)
        self._scene.addItem(node)
        node.moveBy(x, y)

        return node

    def _draw_connection_line(self, left: QGraphicsItem, right: QGraphicsItem):
        left_x = left.pos().x() + GraphNode.WIDTH
        left_y = left.pos().y() + GraphNode.HEIGHT / 2
        right_x = right.pos().x()
        right_y = right.pos().y() + GraphNode.HEIGHT / 2

        connection_line = QGraphicsLineItem(left_x, left_y, right_x, right_y)
        pen = QPen(GraphView.CONNECTION_LINE_COLOR, GraphView.CONNECTION_LINE_THICKNESS)
        connection_line.setPen(pen)
        self._scene.addItem(connection_line)

    def _calc_new_root_coords(self):
        x = GraphView._X
        y = self._root_insertion_y
        self._root_insertion_y += 2 * GraphNode.HEIGHT
        return x, y

    @staticmethod
    def _calc_new_child_coords(parent: QGraphicsItem):
        parent_children_number = parent.data(GraphView._ITEM_DATA_KEYS_DICT["children_number"])
        x = parent.pos().x() + GraphNode.WIDTH + GraphView.HORIZONTAL_GAP
        y = parent.pos().y() + (GraphNode.HEIGHT + GraphView.VERTICAL_GAP) * parent_children_number
        return x, y

    _ITEM_DATA_KEYS_DICT = {
        "children_number" : 0,
        "layer": 1
    }

    _X = 50

    _is_instance = False


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
        cross.clicked.connect(self._receiveNewChildClick)
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

    @pyqtSlot()
    def _receiveNewChildClick(self):
        self.newChildCalled.emit(self)

    newChildCalled = pyqtSignal(QGraphicsItem)


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
