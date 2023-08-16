
from collections import namedtuple
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from settings import *


MultilinePort = namedtuple('MultilinePort', 'multiline portNumber')


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
        self.parentPort = None
        self.childrenLine = None

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


    # Private part
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


# TODO: Calculations of connection points shall be in this module
class ConnectionMultiline(QGraphicsItem):
    # Public interface
    BRANCH_INDENT = 20

    LINE_COLOR = QColorConstants.Red
    LINE_THICKNESS = 3

    class NotAlignedPartners(Exception): pass

    def __init__(self, parent: QGraphicsItem, child: QGraphicsItem):
        if parent.pos().y() != child.pos().y():
            raise ConnectionMultiline.NotAlignedPartners

        super().__init__()

        parent.childrenLine = self
        child.parentPort = MultilinePort(multiline=self, portNumber=1)
        self._width = child.pos().x() - parent.pos().x() - GraphNode.WIDTH
        self._height = ConnectionMultiline.LINE_THICKNESS
        self._lines = []

        parent_connection_point = QPointF(0, 0)
        child_connection_point = QPointF(self._width, 0)
        self._addLine(parent_connection_point, child_connection_point)

    def boundingRect(self) -> QRectF:
        rect = QRectF(0, -ConnectionMultiline.LINE_THICKNESS/2, self._width, self._height)
        return rect

    def paint(self, painter: QPainter=None, *args, **kwargs):
        pen = QPen(ConnectionMultiline.LINE_COLOR, ConnectionMultiline.LINE_THICKNESS)
        painter.setPen(pen)
        for line in self._lines:
            painter.drawLine(line.p1(), line.p2())

    def addChild(self, child: QGraphicsItem):
        self.prepareGeometryChange()

        children_number = self._getChildrenNumber()
        child.parentPort = MultilinePort(multiline=self, portNumber=children_number+1)

        bottom_branch_point = QPointF(ConnectionMultiline.BRANCH_INDENT,
                                      self.mapFromScene(child.pos()).y()+GraphNode.HEIGHT/2)
        if children_number == 1:
            top_branch_point = QPointF(ConnectionMultiline.BRANCH_INDENT, 0)
            self._addLine(top_branch_point, bottom_branch_point)
        else:
            branch_line = self._getBranchLine()
            branch_line.setP2(bottom_branch_point)

        child_local_position = self.mapFromScene(child.pos())
        child_connection_point = QPointF(child_local_position.x(), child_local_position.y() + GraphNode.HEIGHT / 2)
        self._addLine(bottom_branch_point, child_connection_point)

        self._height = child_connection_point.y() + ConnectionMultiline.LINE_THICKNESS/2

    # TODO: Annotate all complex types
    def stretchBelow(self, portNumber, delta_y):
        if portNumber == 0:
            self.moveBy(0, delta_y)
            return

        branch_line = self._getBranchLine()
        branch_line_p2 = branch_line.p2()
        branch_line.setP2(QPointF(branch_line_p2.x(), branch_line_p2.y() + delta_y))

        for child_line in self._lines[portNumber:]:
            child_line_p1 = child_line.p1()
            child_line_p2 = child_line.p2()
            child_line.setPoints(QPointF(child_line_p1.x(), child_line_p1.y() + delta_y),
                                 QPointF(child_line_p2.x(), child_line_p2.y() + delta_y))

        self._width += delta_y


    # Private part
    def _addLine(self, point1: QPointF, point2: QPointF):
        line = QLineF(point1, point2)
        self._lines.append(line)

    def _getChildrenNumber(self):
        if len(self._lines) == 1:
            return 1
        else:
            return len(self._lines)-1

    def _getBranchLine(self) -> QLineF:
        line = self._lines[1]
        return line
