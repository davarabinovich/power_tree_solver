
from settings import *
from tree import *
from graph_gui_int import *

# TODO: Try to separate scene from view creating another class GraphGUI referencing both them
# TODO: Now there is double link between scene objects set and forest - every graph node references to forest node, \
#       and every forest node stores reference to graph node. The second one probably can be deleted.
class GraphView(QGraphicsView):
    # Public interface
    HORIZONTAL_GAP = 50
    VERTICAL_GAP = 50
    VERTICAL_STEP = VERTICAL_GAP + GraphNode.HEIGHT
    HORIZONTAL_STEP = HORIZONTAL_GAP + GraphNode.WIDTH

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
        self._scene = QGraphicsScene()
        self.setScene(self._scene)

        cross = CrossIcon()
        self._scene.addItem(cross)
        cross.moveBy(GraphView.CROSS_X, GraphView.CROSS_Y)
        cross.clicked.connect(self.addRoot)

        self._forest = Forest()
        self.addRoot()


    @pyqtSlot()
    def addRoot(self):
        position = self._calcNewRootPosition()
        root = self._createNodeOnScene(position)
        forest_node = self._forest.create_root(root)
        GraphView._setNodesField(root, "forest_node", forest_node)

    # TODO: replace QGraphicsItem with GraphNode
    # TODO: try to convert GraphNode to Tree::Node implicitly (to send parent to add_leaf instead parent_forest_node; \
    #       it also requires to change Forest methods' signatures - not internal _ForestNode, but visible for user Node
    @pyqtSlot(QGraphicsItem)
    def addChild(self, parent: QGraphicsItem):
        parent_forest_node = GraphView._getNodesField(parent, "forest_node")
        if len(parent_forest_node.successors) > 0:
            last_parent_child = parent_forest_node.successors[-1]
            self._moveNodesBelow(last_parent_child)

        position = GraphView._calcNewChildPosition(parent)
        child = self._createNodeOnScene(position)
        parent_forest_node = GraphView._getNodesField(parent, "forest_node")
        forest_node = self._forest.add_leaf(parent_forest_node, child)
        GraphView._setNodesField(child, "forest_node", forest_node)

        self._drawConnectionLine(parent, child)


    # Private interface
    _NODE_DATA_KEYS_DICT = {
        "forest_node": 0,
        "layer": 1,
        "parent": 2
    }

    _LINE_DATA_KEYS_DICT = {
        "parent": 0,
        "child": 1
    }

    def _createNodeOnScene(self, position: QPointF) -> GraphNode:
        graph_node = GraphNode()
        graph_node.newChildCalled.connect(self.addChild)
        self._scene.addItem(graph_node)
        graph_node.moveBy(position.x(), position.y())
        return graph_node

    def _drawConnectionLine(self, left: QGraphicsItem, right: QGraphicsItem):
        left_point = GraphView._calcConnectionPointForLeft(left)
        right_point = GraphView._calcConnectionPointForRight(right)
        connection_line = QGraphicsLineItem(left_point.x(), left_point.y(), right_point.x(), right_point.y())

        pen = QPen(GraphView.CONNECTION_LINE_COLOR, GraphView.CONNECTION_LINE_THICKNESS)
        connection_line.setPen(pen)
        self._scene.addItem(connection_line)

    def _moveNodesBelow(self, node: Node):
        node_forest_root = self._forest.find_root(node)
        root_index = self._forest.roots.index(node_forest_root)
        for root in self._forest.roots[root_index+1:]:
            self._moveSubtreeBelow(root)

        ancestors = self._forest.get_path_to_root(node)
        for ancestor in reversed(ancestors):
            ancestor_index = ancestor.index_by_parent()
            for following_ancestor in ancestor.parent.successors[ancestor_index+1:]:
                self._moveSubtreeBelow(following_ancestor)


    def _moveNodeBelow(self, node: GraphNode):
        delta_y = GraphView.VERTICAL_GAP + GraphNode.HEIGHT
        node.moveBy(0, delta_y)
        GraphView._incNodesField(node, "layer")

    def _redrawConnectionLine(self, line: QGraphicsLineItem):
        parent = line.data(GraphView._LINE_DATA_KEYS_DICT["parent"])
        parent_x, parent_y = GraphView._calcConnectionPointForLeft(parent)
        child = line.data(GraphView._LINE_DATA_KEYS_DICT["child"])
        child_x, child_y = GraphView._calcConnectionPointForRight(child)
        line.setLine(parent_x, parent_y, child_x, child_y)


    @staticmethod
    def _calcNewChildPosition(parent: QGraphicsItem) -> QPointF:
        x = parent.pos().x() +  GraphView.HORIZONTAL_STEP
        parent_forest_node = GraphView._getNodesField(parent, "forest_node")
        parent_children_num = len(parent_forest_node.successors)
        y = parent.pos().y() + parent_children_num * GraphView.VERTICAL_STEP
        return QPointF(x, y)

    @staticmethod
    def _calcConnectionPointForLeft(item: QGraphicsItem) -> QPointF:
        x = item.pos().x() + GraphNode.WIDTH
        y = item.pos().y() + GraphNode.HEIGHT / 2
        return QPointF(x, y)

    @staticmethod
    def _calcConnectionPointForRight(item: QGraphicsItem) -> QPointF:
        x = item.pos().x()
        y = item.pos().y() + GraphNode.HEIGHT / 2
        return QPointF(x, y)

    def _calcNewRootPosition(self) -> QPointF:
        x = GraphView.HORIZONTAL_GAP
        layer = self._forest.calc_width() + 1
        y = GraphView.VERTICAL_GAP + layer * GraphView.VERTICAL_STEP
        return QPointF(x, y)


    @staticmethod
    def _setNodesField(node: QGraphicsItem, key, value):
        node.setData(GraphView._NODE_DATA_KEYS_DICT[key], value)

    @staticmethod
    def _incNodesField(node: QGraphicsItem, key):
        cur_value = GraphView._getNodesField(node, key)
        if type(cur_value) is not int:
            raise ValueError
        node.setData(GraphView._NODE_DATA_KEYS_DICT[key], cur_value + 1)

    @staticmethod
    def _getNodesField(node: QGraphicsItem, key):
        return node.data(GraphView._NODE_DATA_KEYS_DICT[key])

    def _moveSubtreeBelow(self, subroot: Node):
        graph_subroot = subroot.content
        connection_line = self._scene.itemAt(GraphView._calcConnectionPointForRight(graph_subroot), QTransform())
        graph_subroot.moveBy(0, GraphView.VERTICAL_STEP)

        if subroot.is_successor():
            left_point = GraphView._calcConnectionPointForLeft(subroot.parent.content)
            right_point = GraphView._calcConnectionPointForRight(graph_subroot)
            if isinstance(connection_line, QGraphicsLineItem):
                connection_line.setLine(left_point.x(), left_point.y(), right_point.x(), right_point.y())

        for successor in subroot.successors:
            self._moveSubtreeBelow(successor)


    _is_instance = False
