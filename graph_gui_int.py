
from collections import namedtuple
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *

from settings import *
from source_node import *


MultilinePort = namedtuple('MultilinePort', 'multiline portNumber')


class GraphNode(QGraphicsObject):
    # Public interface
    WIDTH = 200
    HEIGHT = 75
    ROUNDING = 10

    FILLING_COLOR = QColorConstants.Black
    OUTLINE_COLOR = QColorConstants.Yellow
    OUTLINE_THICKNESS = 5
    HALF_OUTLINE_THICKNESS = OUTLINE_THICKNESS / 2

    CROSS_GAP = 5

    WIDGET_VERTICAL_GAP = 5
    WIDGET_HORIZONTAL_GAP = 5
    WIDGET_STEP = 50

    def __init__(self, widget: QWidget, side_widgets: list):
        super().__init__(None)
        self.parentPort = None
        self.childrenLine = None

        proxy_widget = QGraphicsProxyWidget(self)
        proxy_widget.setWidget(widget)
        proxy_widget.moveBy(GraphNode.WIDGET_HORIZONTAL_GAP, GraphNode.WIDGET_VERTICAL_GAP)

        side_widget_points = GraphNode._calcSideWidgetsCoords(len(side_widgets))
        max_widget_width = 0
        for index in range(len(side_widgets)):
            widget = side_widgets[index]
            widget.setParentItem(self)
            widget.moveBy(side_widget_points[index].x(), side_widget_points[index].y())

            widget_width = widget.getWidthWithText()
            if widget_width > max_widget_width:
                max_widget_width = widget_width

        self._width = GraphNode.WIDTH + GraphNode.CROSS_GAP + max_widget_width

    def boundingRect(self) -> QRectF:
        top_left_point = QPointF(-GraphNode.HALF_OUTLINE_THICKNESS, -GraphNode.HALF_OUTLINE_THICKNESS)
        bottom_right_point = QPointF(self._width, GraphNode.HEIGHT+GraphNode.HALF_OUTLINE_THICKNESS)
        rect = QRectF(top_left_point, bottom_right_point)
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

    @staticmethod
    def _calcSideWidgetsCoords(side_widgets_num):
        coords = []
        for index in range(side_widgets_num):
            coord = QPointF(GraphNode.WIDTH + GraphNode.WIDGET_HORIZONTAL_GAP,
                            GraphNode.WIDGET_VERTICAL_GAP + index * GraphNode.WIDGET_STEP)
            coords.append(coord)
        return coords


class CrossIcon(QGraphicsWidget):
    # Public interface
    DIAMETER = 12
    LINE_LENGTH = 8

    CIRCLE_COLOR = QColorConstants.Green
    LINE_COLOR = QColorConstants.White
    LINE_THICKNESS = 3

    TEXT_POINT_SIZE = 9
    TEXT_HORIZONTAL_GAP = 3
    TEXT_VERTICAL_GAP = -2

    LINE_GAP = (DIAMETER - LINE_LENGTH) / 2
    RADIUS = DIAMETER / 2

    def __init__(self, parent: QGraphicsItem=None, label: str=""):
        super().__init__(parent)

        label = QGraphicsSimpleTextItem(label, self)
        font = label.font()
        font.setPointSize(CrossIcon.TEXT_POINT_SIZE)
        label.setFont(font)

        label.moveBy(CrossIcon.DIAMETER + CrossIcon.TEXT_HORIZONTAL_GAP, CrossIcon.TEXT_VERTICAL_GAP)
        self._label_width = label.boundingRect().width()

    def boundingRect(self) -> QRectF:
        if self._label_width < CrossIcon.DIAMETER:
            width = CrossIcon.DIAMETER
        else:
            width = self._label_width
        rect = QRectF(0, 0, width, CrossIcon.DIAMETER)
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

    def getWidthWithText(self):
        if self._label_width < CrossIcon.DIAMETER:
            width = CrossIcon.DIAMETER
        else:
            width = self._label_width
        return width

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
