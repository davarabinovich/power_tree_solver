
from __future__ import annotations
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *


# TODO: Try to separate scene from view creating another class GraphGUI referencing both them
class GraphView(QGraphicsView):
    # Public interface
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
        cross.clicked.connect(self.addRoot)

        self.addRoot()


    @pyqtSlot()
    def addRoot(self):
        x_pos, layer = self._calcNewRootPosition()
        self._addNode(x_pos, layer)

    # TODO: replace QGraphicsItem with GraphNode
    @pyqtSlot(QGraphicsItem)
    def addChild(self, parent: QGraphicsItem):
        x_pos, layer = GraphView._calcNewChildPosition(parent)
        parent_children_number = GraphView._getNodesField(parent,"children_number")
        if parent_children_number > 0:
            self._moveNodesBelow(layer)

        child = self._addNode(x_pos, layer)
        GraphView._setNodesField(child, "parent", parent)
        GraphView._incNodesField(parent, "children_number")
        self._drawConnectionLine(parent, child)


    # Private interface
    _ITEM_DATA_KEYS_DICT = {
        "children_number": 0,
        "layer": 1,
        "connection_line": 2,
        "parent": 3
    }

    def _addNode(self, x_pos, layer):
        node = GraphNode()
        GraphView._setNodesField(node, "children_number", 0)
        node.newChildCalled.connect(self.addChild)
        self._scene.addItem(node)

        y_pos = GraphView.VERTICAL_GAP + layer * (GraphNode.HEIGHT + GraphView.VERTICAL_GAP)
        node.moveBy(x_pos, y_pos)

        if layer == len(self._nodes):
            self._nodes.append([])
        self._nodes[layer].append(node)
        GraphView._setNodesField(node, "layer", layer)
        return node

    def _drawConnectionLine(self, left: QGraphicsItem, right: QGraphicsItem):
        left_x, left_y = GraphView._calcConnectionPointForLeft(left)
        right_x, right_y = GraphView._calcConnectionPointForRight(right)
        connection_line = QGraphicsLineItem(left_x, left_y, right_x, right_y)

        pen = QPen(GraphView.CONNECTION_LINE_COLOR, GraphView.CONNECTION_LINE_THICKNESS)
        connection_line.setPen(pen)
        self._scene.addItem(connection_line)
        GraphView._setNodesField(right, "connection_line", connection_line)

    def _moveNodesBelow(self, layer):
        if (layer < len(self._nodes)):
            self._nodes.insert(layer, [])

        for cur_layer in range(layer+1, len(self._nodes)):
            for node in self._nodes[cur_layer]:
                GraphView._moveNodeWithLineBelow(node)

    @staticmethod
    def _moveNodeWithLineBelow(node):
        delta_y = GraphView.VERTICAL_GAP + GraphNode.HEIGHT
        node.moveBy(0, delta_y)
        GraphView._incNodesField(node, "layer")
        if GraphView._getNodesField(node, "parent") is not None:
            GraphView._redrawConnectionLine(node)

    @staticmethod
    def _redrawConnectionLine(node):
        connection_line = GraphView._getNodesField(node, "connection_line")
        left_x, left_y = GraphView._calcConnectionPointForLeft(GraphView._getNodesField(node, "parent"))
        right_x, right_y = GraphView._calcConnectionPointForRight(node)
        connection_line.setLine(left_x, left_y, right_x, right_y)


    @staticmethod
    def _calcNewChildPosition(parent: QGraphicsItem):
        x_pos = parent.pos().x() + GraphNode.WIDTH + GraphView.HORIZONTAL_GAP
        parent_children_number = GraphView._getNodesField(parent, "children_number")
        parent_layer = GraphView._getNodesField(parent, "layer")
        layer = parent_layer + parent_children_number
        return x_pos, layer

    @staticmethod
    def _calcConnectionPointForLeft(item: QGraphicsItem):
        x = item.pos().x() + GraphNode.WIDTH
        y = item.pos().y() + GraphNode.HEIGHT / 2
        return x, y

    @staticmethod
    def _calcConnectionPointForRight(item: QGraphicsItem):
        x = item.pos().x()
        y = item.pos().y() + GraphNode.HEIGHT / 2
        return x, y

    def _calcNewRootPosition(self):
        x_pos = GraphView.HORIZONTAL_GAP
        layer = len(self._nodes)
        return x_pos, layer


    @staticmethod
    def _setNodesField(node: QGraphicsItem, key, value):
        node.setData(GraphView._ITEM_DATA_KEYS_DICT[key], value)

    @staticmethod
    def _incNodesField(node: QGraphicsItem, key):
        cur_value = GraphView._getNodesField(node, key)
        if type(cur_value) is not int:
            raise ValueError
        node.setData(GraphView._ITEM_DATA_KEYS_DICT[key], cur_value+1)

    @staticmethod
    def _getNodesField(node: QGraphicsItem, key):
        return node.data(GraphView._ITEM_DATA_KEYS_DICT[key])


    _is_instance = False


class GraphNode(QGraphicsObject):
    # Public interface
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

    newChildCalled = pyqtSignal(QGraphicsItem)


    # Private interface
    @pyqtSlot()
    def _receiveNewChildClick(self):
        self.newChildCalled.emit(self)


class CrossIcon(QGraphicsWidget):
    # Public interface
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
