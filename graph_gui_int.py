
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

    # TODO: This module doesn't know about scene, but this functions invokes pos(), that assumes, that scene is set.
    #       need to invent correct way to place and use this code
    def calcConnectionPointForParent(self) -> QPointF:
        x = self.pos().x() + GraphNode.WIDTH
        y = self.pos().y() + GraphNode.HEIGHT / 2
        return QPointF(x, y)

    def calcConnectionPointForChild(self) -> QPointF:
        x = self.pos().x()
        y = self.pos().y() + GraphNode.HEIGHT / 2
        return QPointF(x, y)

    def calcBranchPointForParent(self) -> QPointF:
        x = self.pos().x() + GraphNode.WIDTH + ConnectionMultiline.BRANCH_INDENT
        y = self.pos().y() + GraphNode.HEIGHT / 2
        return QPointF(x, y)


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


class ConnectionMultiline():
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
        self._lines = []

        parent_connection_point = parent.calcConnectionPointForParent()
        child_connection_point = child.calcConnectionPointForChild()
        self._addLine(parent_connection_point, child_connection_point)

    def addChild(self, child: QGraphicsItem):
        children_number = self._getChildrenNumber()
        child.parentPort = MultilinePort(multiline=self, portNumber=children_number+1)

        branch_x = self._lines[0].line().p1().x() + ConnectionMultiline.BRANCH_INDENT
        bottom_branch_point = QPointF(branch_x, child.calcConnectionPointForChild().y())

        if children_number == 1:
            top_branch_point = self._getTopBranchPoint()
            self._addLine(top_branch_point, bottom_branch_point)
        else:
            branch_line = self._getBranchLine()
            branch_qlinef = branch_line.line()
            branch_qlinef.setP2(bottom_branch_point)
            branch_line.setLine(branch_qlinef)

        self._addLine(bottom_branch_point, child.calcConnectionPointForChild())

    # TODO: Annotate all complex types
    def stretchBelow(self, portNumber, delta_y):
        if portNumber == 0:
            return

        branch_line = self._getBranchLine()
        branch_qlinef = branch_line.line()
        branch_qlinef.setP2(QPointF(branch_qlinef.p2().x(), branch_qlinef.p2().y() + delta_y))
        branch_line.setLine(branch_qlinef)

        for child_line in self._lines[portNumber:]:
            child_line_p1 = child_line.line().p1()
            child_line_p2 = child_line.line().p2()
            child_line.setLine(child_line_p1.x(), child_line_p1.y() + delta_y,
                               child_line_p2.x(), child_line_p2.y() + delta_y)

    def callForAllLines(self, method_name: str, *args):
        for line in self._lines:
            method = getattr(line, method_name)
            method(*args)

    def getNewLines(self) -> list:
        children_number = self._getChildrenNumber()
        if children_number == 1:
            return [self._lines[0]]
        elif children_number == 2:
            return [self._lines[1], self._lines[2]]
        else:
            return [self._lines[-1]]


    # Private part
    def _addLine(self, point1: QPointF, point2: QPointF):
        line = QGraphicsLineItem(point1.x(), point1.y(), point2.x(), point2.y())
        self._lines.append(line)
        pen = QPen(ConnectionMultiline.LINE_COLOR, ConnectionMultiline.LINE_THICKNESS)
        line.setPen(pen)

    def _getChildrenNumber(self):
        if len(self._lines) == 1:
            return 1
        else:
            return len(self._lines)-1

    def _getFirstLine(self) -> QGraphicsLineItem:
        line = self._lines[0]
        return line

    def _getBranchLine(self) -> QGraphicsLineItem:
        line = self._lines[1]
        return line

    def _getTopBranchPoint(self) -> QPointF:
        first_line = self._getFirstLine().line()
        top_branch_point_x = first_line.p1().x() + ConnectionMultiline.BRANCH_INDENT
        top_branch_point_y = first_line.p1().y()
        top_branch_point = QPointF(top_branch_point_x, top_branch_point_y)
        return top_branch_point
