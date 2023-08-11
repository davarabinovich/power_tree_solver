
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

    CONNECTION_LINE_COLOR = QColorConstants.Red
    CONNECTION_LINE_THICKNESS = 3

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
        rect.setData(GraphView._ITEM_DATA_KEYS_DICT["children_number"], 0)
        rect.newChildCalled.connect(self.add_child)
        self._scene.addItem(rect)
        x, y = self._calc_new_root_coords()
        rect.moveBy(x, y)

    @pyqtSlot(QGraphicsItem)
    def add_child(self, parent: QGraphicsItem):
        child = GraphNode()
        child.setData(GraphView._ITEM_DATA_KEYS_DICT["children_number"], 0)
        self._scene.addItem(child)
        parent_children_number = parent.data(GraphView._ITEM_DATA_KEYS_DICT["children_number"])
        x = parent.pos().x() + GraphNode.WIDTH + GraphView.HORIZONTAL_GAP
        y = parent.pos().y() + (GraphNode.HEIGHT + GraphView.VERTICAL_GAP) * parent_children_number
        child.moveBy(x, y)
        parent.setData(GraphView._ITEM_DATA_KEYS_DICT["children_number"], parent_children_number+1)
        child.newChildCalled.connect(self.add_child)

        parent_x = parent.pos().x() + GraphNode.WIDTH
        parent_y = parent.pos().y() + GraphNode.HEIGHT/2
        child_x = x
        child_y = y + GraphNode.HEIGHT/2
        connection_line = QGraphicsLineItem(parent_x, parent_y, child_x, child_y)
        pen = QPen(GraphView.CONNECTION_LINE_COLOR, GraphView.CONNECTION_LINE_THICKNESS)
        connection_line.setPen(pen)
        self._scene.addItem(connection_line)


    def _calc_new_root_coords(self):
        x = GraphView._X
        y = self._root_insertion_y
        self._root_insertion_y += 2 * GraphNode.HEIGHT
        return x, y

    _ITEM_DATA_KEYS_DICT = {
        "children_number" : 0
    }

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
