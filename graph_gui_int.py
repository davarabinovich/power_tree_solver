
from __future__ import annotations
from recordclass import recordclass
from math import *

from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *


NodePortToParent = recordclass('NodePortToParent', 'multiline portNumber')  # Port numbers start from 1
MultilinePort = recordclass('MultilinePort', 'line node')


class GraphNode(QGraphicsObject):
    # Public interface
    WIDTH = 200
    HEIGHT = 140
    ROUNDING = 10

    FILLING_COLOR = QColorConstants.Black
    OUTLINE_COLOR = QColorConstants.Yellow
    OUTLINE_THICKNESS = 5
    HALF_OUTLINE_THICKNESS = OUTLINE_THICKNESS / 2

    CROSS_GAP = 5

    WIDGET_VERTICAL_GAP = 5
    WIDGET_HORIZONTAL_GAP = 5
    WIDGET_STEP = 90

    def __init__(self, widget: QWidget=None, side_widgets: list[SideWidget]=None):
        super().__init__(None)
        self.parentPort = None
        self.childrenLine = None

        proxy_widget = QGraphicsProxyWidget(self)
        proxy_widget.setWidget(widget)
        proxy_widget.moveBy(GraphNode.WIDGET_HORIZONTAL_GAP, GraphNode.WIDGET_VERTICAL_GAP)

        if side_widgets is not None:
            side_widget_points = GraphNode._calcSideWidgetsCoords(len(side_widgets))
            max_widget_width = 0
            for index in range(len(side_widgets)):
                widget = side_widgets[index]
                widget.setParentItem(self)
                widget.moveBy(side_widget_points[index].x(), side_widget_points[index].y())
                widget.clicked.connect(self._receiveSideWidgetClick)

                widget_width = widget.getWidthWithText()
                if widget_width > max_widget_width:
                    max_widget_width = widget_width

            self._width = GraphNode.WIDTH + GraphNode.CROSS_GAP + max_widget_width
        else:
            self._width = GraphNode.WIDTH

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

    sideWidgetClicked = pyqtSignal('PyQt_PyObject', int, name='sideWidgetClicked')

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
    @pyqtSlot('PyQt_PyObject')
    def _receiveSideWidgetClick(self, side_widget: PlusIcon):
        side_widgets = self.childItems()
        widget_num = side_widgets.index(side_widget) - 1
        self.sideWidgetClicked.emit(self, widget_num)

    @staticmethod
    def _calcSideWidgetsCoords(side_widgets_num):
        side_widget_x = GraphNode.WIDTH + GraphNode.WIDGET_HORIZONTAL_GAP
        first_coord = QPointF(side_widget_x, 0)
        second_coord = QPointF(side_widget_x, GraphNode.HEIGHT / 2 + SideWidget.DIAMETER)
        third_coord = QPointF(side_widget_x, GraphNode.HEIGHT - SideWidget.DIAMETER)

        coords = [first_coord, second_coord, third_coord]
        return coords[:side_widgets_num]


class SideWidget(QGraphicsWidget):
    DIAMETER = 12
    RADIUS = DIAMETER / 2
    TEXT_POINT_SIZE = 9
    TEXT_HORIZONTAL_GAP = 3
    TEXT_VERTICAL_GAP = -2

    def __init__(self, parent: GraphNode=None, label: str=""):
        super().__init__(parent)

        self._label = QGraphicsSimpleTextItem(label, self)
        font = self._label.font()
        font.setPointSize(SideWidget.TEXT_POINT_SIZE)
        self._label.setFont(font)
        self._label.moveBy(SideWidget.DIAMETER + SideWidget.TEXT_HORIZONTAL_GAP, SideWidget.TEXT_VERTICAL_GAP)

    def boundingRect(self) -> QRectF:
        width = self.getWidthWithText()
        rect = QRectF(0, 0, width, SideWidget.DIAMETER)
        return rect

    def getWidthWithText(self):
        width = SideWidget.DIAMETER + SideWidget.TEXT_HORIZONTAL_GAP + self._label.boundingRect().width()
        return width

    def mousePressEvent(self, event, QGraphicsSceneMouseEvent=None):
        self.clicked.emit(self)

    clicked = pyqtSignal('PyQt_PyObject', name='clicked')


class PlusIcon(SideWidget):
    LINE_LENGTH = 8
    LINE_GAP = (SideWidget.DIAMETER - LINE_LENGTH) / 2
    CIRCLE_COLOR = QColorConstants.Green
    LINE_COLOR = QColorConstants.White
    LINE_THICKNESS = 3

    def __init__(self, parent: GraphNode=None, label: str=""):
        super().__init__(parent, label)

    def paint(self, painter: QPainter=None, *args, **kwargs):
        pen = QPen(PlusIcon.CIRCLE_COLOR, 0)
        brush = QBrush(PlusIcon.CIRCLE_COLOR)
        painter.setPen(pen)
        painter.setBrush(brush)
        painter.drawEllipse(0, 0, PlusIcon.DIAMETER, PlusIcon.DIAMETER)

        pen = QPen(PlusIcon.LINE_COLOR, PlusIcon.LINE_THICKNESS)
        painter.setPen(pen)
        top_point = QPointF(PlusIcon.RADIUS, PlusIcon.LINE_GAP)
        bottom_point = QPointF(PlusIcon.RADIUS, PlusIcon.DIAMETER - PlusIcon.LINE_GAP)
        painter.drawLine(top_point, bottom_point)

        left_point = QPointF(PlusIcon.LINE_GAP, PlusIcon.RADIUS)
        right_point = QPointF(PlusIcon.DIAMETER - PlusIcon.LINE_GAP, PlusIcon.RADIUS)
        painter.drawLine(left_point, right_point)


class CrossIcon(SideWidget):
    LINE_LENGTH = 8
    LINE_GAP = (SideWidget.DIAMETER - LINE_LENGTH/sqrt(2)) / 2
    CIRCLE_COLOR = QColorConstants.Red
    LINE_COLOR = QColorConstants.White
    LINE_THICKNESS = 3

    def __init__(self, parent: GraphNode=None, label: str=""):
        super().__init__(parent, label)

    def paint(self, painter: QPainter=None, *args, **kwargs):
        pen = QPen(CrossIcon.CIRCLE_COLOR, 0)
        brush = QBrush(CrossIcon.CIRCLE_COLOR)
        painter.setPen(pen)
        painter.setBrush(brush)
        painter.drawEllipse(0, 0, CrossIcon.DIAMETER, CrossIcon.DIAMETER)

        near_coord = CrossIcon.LINE_GAP
        far_coord = CrossIcon.DIAMETER - CrossIcon.LINE_GAP

        pen = QPen(PlusIcon.LINE_COLOR, PlusIcon.LINE_THICKNESS)
        painter.setPen(pen)
        first_point = QPointF(near_coord, near_coord)
        second_point = QPointF(far_coord, far_coord)
        painter.drawLine(first_point, second_point)

        first_point = QPointF(near_coord, far_coord)
        second_point = QPointF(far_coord, near_coord)
        painter.drawLine(first_point, second_point)


class ConnectionMultiline:
    # Public interface
    BRANCH_INDENT = 100

    LINE_COLOR = QColorConstants.Red
    LINE_THICKNESS = 3

    class NotAlignedPartners(Exception): pass

    def __init__(self, parent: GraphNode, child: GraphNode):
        if parent.pos().y() != child.pos().y():
            raise ConnectionMultiline.NotAlignedPartners

        super().__init__()
        self._scene: QGraphicsScene = parent.scene()
        self._parent = parent  # TODO: Use it, if it will be saved after refactoring
        self._children_ports = []
        self._parent_line = None
        self._branch_line = None

        # TODO: Try to implement lines indexing via an iterable data structure of 'dense set' with random access
        #       based on binary search
        parent.childrenLine = self
        child.parentPort = NodePortToParent(multiline=self, portNumber=1)

        parent_connection_point = parent.calcConnectionPointForParent()
        branch_point = QPointF(parent_connection_point.x() + ConnectionMultiline.BRANCH_INDENT,
                               parent_connection_point.y())
        child_connection_point = child.calcConnectionPointForChild()
        self._parent_line = self._drawLine(parent_connection_point, branch_point)
        self._addChildLine(parent_connection_point, child_connection_point, child)

    def addChild(self, child: GraphNode):
        children_number = self._getChildrenNumber()
        child.parentPort = NodePortToParent(multiline=self, portNumber=children_number + 1)

        top_branch_point = self._parent_line.line().p2()
        bottom_branch_point = QPointF(top_branch_point.x(), child.calcConnectionPointForChild().y())

        if children_number == 1:
            self._branch_line = self._drawLine(top_branch_point, bottom_branch_point)
        else:
            branch_qlinef = self._branch_line.line()
            branch_qlinef.setP2(bottom_branch_point)
            self._branch_line.setLine(branch_qlinef)

        self._addChildLine(bottom_branch_point, child.calcConnectionPointForChild(), child)

    def deleteChild(self, port_number):  # Port numbers starts from 1
        initial_children_number = self._getChildrenNumber()

        child_line = self._children_ports[port_number-1].line
        self._scene.removeItem(child_line)

        self._children_ports.pop(port_number-1)
        for port in self._children_ports[port_number-1:]:
            child = port.node
            child.parentPort.portNumber = child.parentPort.portNumber - 1

        if port_number == initial_children_number:
            if initial_children_number > 2:
                last_child_line_start = self._children_ports[-1].line.line().p1()
                branch_qlinef = self._branch_line.line()
                branch_qlinef.setP2(last_child_line_start)
                self._branch_line.setLine(branch_qlinef)
            elif initial_children_number == 2:
                self._scene.removeItem(self._branch_line)
            else:
                self._scene.removeItem(self._parent_line)
                self._parent.childrenLine = None

    def insertChildren(self, portNumber):  # Port numbers starts from 1
        parent = self._children_ports[portNumber - 1].node
        children_ports = parent.childrenLine._children_ports

        parent_child_line = self._children_ports[portNumber-1].line
        self._scene.removeItem(parent_child_line)

        parent_to_children_multiline = parent.childrenLine
        parent_parent_line = parent_to_children_multiline._parent_line
        self._scene.removeItem(parent_parent_line)

        if parent_to_children_multiline._branch_line is not None:
            if self._branch_line is not None:
                parent_branch_line = parent_to_children_multiline._branch_line
                self._scene.removeItem(parent_branch_line)
            else:
                branch_line_start = self._parent.calcBranchPointForParent()
                branch_line_finish = QPointF(branch_line_start.x(),
                                             children_ports[-1].node.calcConnectionPointForChild().y())
                self._branch_line = self._drawLine(branch_line_start, branch_line_finish)
        else:
            if self._branch_line is None and len(children_ports) > 1:
                branch_line_start = self._parent.calcBranchPointForParent()
                branch_line_finish = QPointF(branch_line_start.x(),
                                             children_ports[-1].node.calcConnectionPointForChild().y())
                self._branch_line = self._drawLine(branch_line_start, branch_line_finish)

        new_line_start_x = self._children_ports[0].line.p1().x()
        new_line_finish_x = self._children_ports[0].line.p2().x()
        for port in children_ports:
            line = port.line
            qlinef = line.line()
            qlinef.setP1(new_line_start_x, qlinef.p1().y())
            qlinef.setP2(new_line_finish_x, qlinef.p2().y())
            line.setLine(qlinef)

        self._children_ports = children_ports + self._children_ports

        for port in children_ports:
            child_parent_port = port.node.parentPort
            child_parent_port.multiline = self

        for child_index in range(len(self._children_ports)):
            child_parent_port = self._children_ports[child_index]
            child_parent_port.portNumber = child_index + 1

    # TODO: Annotate all complex types
    def stretch(self, portNumber, delta_y):
        if portNumber < 2:
            return

        if portNumber == 2:
            self._scene.removeItem(self._branch_line)
            self._branch_line = None
        else:
            branch_qlinef = self._branch_line.line()
            branch_qlinef.setP2(QPointF(branch_qlinef.p2().x(), branch_qlinef.p2().y() + delta_y))
            self._branch_line.setLine(branch_qlinef)

        for port in self._children_ports[portNumber-1:]:
            child_line_p1 = port.line.line().p1()
            child_line_p2 = port.line.line().p2()
            port.line.setLine(child_line_p1.x(), child_line_p1.y() + delta_y,
                              child_line_p2.x(), child_line_p2.y() + delta_y)

    # TODO: Replace with simple moveBy method
    def callForAllLines(self, method_name: str, *args):
        for port in self._children_ports:
            method = getattr(port.line, method_name)
            method(*args)

        method = getattr(self._parent_line, method_name)
        method(*args)

        if self._branch_line is not None:
            method = getattr(self._branch_line, method_name)
            method(*args)

    # Private part
    def _addChildLine(self, point1: QPointF, point2: QPointF, child: GraphNode):
        line = self._drawLine(point1, point2)
        self._children_ports.append(MultilinePort(line, child))

    def _drawLine(self, point1: QPointF, point2: QPointF) -> QGraphicsLineItem:
        line = QGraphicsLineItem(point1.x(), point1.y(), point2.x(), point2.y())
        pen = QPen(ConnectionMultiline.LINE_COLOR, ConnectionMultiline.LINE_THICKNESS)
        line.setPen(pen)
        self._scene.addItem(line)
        return line

    def _getChildrenNumber(self):
        children_number = len(self._children_ports)
        return children_number
