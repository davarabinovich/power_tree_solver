
# Plan of reworking:
# To try:
#     - manual control of scene rect
#     - use different view updating policy (method, see GraphicsView reference, BSP tree)

from settings import *
from tree import *
from graph_gui_int import *

# TODO: Try to separate scene from view creating another class GraphGUI referencing both them
# TODO: Now there is double link between scene objects set and forest - every graph node references to forest node, \
#       and every forest node stores reference to graph node. The second one probably can be deleted.
class GraphView(QGraphicsView):
    # Public interface
    HORIZONTAL_GAP = 150
    VERTICAL_GAP = 50
    VERTICAL_STEP = VERTICAL_GAP + GraphNode.HEIGHT
    HORIZONTAL_STEP = HORIZONTAL_GAP + GraphNode.WIDTH

    LINE_COLOR = QColorConstants.Red
    LINE_THICKNESS = 3


    def __init__(self, parent: QWidget=None):
        super().__init__(parent)

        # TODO: Try to delete
        self._scene = QGraphicsScene()
        self.setScene(self._scene)
        self._forest = Forest()


    nodeSideWidgetClicked = pyqtSignal('PyQt_PyObject', int, name='nodeSideWidgetClicked')


    def addCross(self, position: QPointF) -> PlusIcon:
        cross = PlusIcon()
        self._scene.addItem(cross)
        cross.moveBy(position.x(), position.y())
        return cross

    def addRoot(self, widget: QWidget=None, side_widgets: list=None) -> GraphNode:
        position = self._calcNewRootPosition()
        root = self._createNodeOnScene(position, widget, side_widgets)
        forest_node = self._forest.create_root()
        self._linkGraphAndForestNodes(root, forest_node)
        return root

    # TODO: replace QGraphicsItem with GraphNode
    # TODO: try to convert GraphNode to Tree::Node implicitly (to send parent to add_leaf instead parent_forest_node;
    #       it also requires to change Forest methods' signatures - not internal _ForestNode, but visible for user Node
    def addChild(self, parent: GraphNode, widget: QWidget=None, side_widgets: list[SideWidget]=None) -> GraphNode:
        parent_forest_node = parent.data(GraphView._FOREST_NODE_DATA_KEY)
        if len(parent_forest_node.successors) > 0:
            furthest_parent_leaf = self._forest.find_furthest_leaf(parent_forest_node)
            self._moveNodesBelow(furthest_parent_leaf)

        position = GraphView._calcNewChildPosition(parent)
        child = self._createNodeOnScene(position, widget, side_widgets)
        forest_node = self._forest.add_leaf(parent_forest_node)
        self._linkGraphAndForestNodes(child, forest_node)
        self._drawConnection(parent, child)

        return child

    def deleteNode(self, graph_node: GraphNode):
        forest_node: Forest.ForestNode = graph_node.data(GraphView._FOREST_NODE_DATA_KEY)
        self._moveNodesAbove(forest_node)
        graph_node.parentPort.multiline.deleteChild(graph_node.parentPort.portNumber)
        if forest_node.is_leaf():
            self._forest.delete_leaf(forest_node)
        self._scene.removeItem(graph_node)

    def reset(self):
        self._scene.clear()
        self._forest = Forest()


    # Private interface
    _FOREST_NODE_DATA_KEY = 0


    class _DrawingConnectionLineToNothing(Exception): pass


    @staticmethod
    def _linkGraphAndForestNodes(graph_node: GraphNode, forest_node: Node):
        forest_node.content = graph_node
        graph_node.setData(GraphView._FOREST_NODE_DATA_KEY, forest_node)

    @staticmethod
    def _calcNewChildPosition(parent: GraphNode) -> QPointF:
        x = parent.pos().x() +  GraphView.HORIZONTAL_STEP

        parent_forest_node = parent.data(GraphView._FOREST_NODE_DATA_KEY)
        if parent_forest_node.is_leaf():
            delta_y = 0
        else:
            parent_width = parent_forest_node.calc_subtree_width()
            delta_y = parent_width * GraphView.VERTICAL_STEP
        y = parent.pos().y() + delta_y

        return QPointF(x, y)


    # TODO: Need to tune node's dimensions, boundingRect
    def _createNodeOnScene(self, position: QPointF, widget: QWidget=None, side_widgets: list=None) -> GraphNode:
        graph_node = GraphNode(widget, side_widgets)
        graph_node.sideWidgetClicked.connect(self.nodeSideWidgetClicked)
        self._scene.addItem(graph_node)
        graph_node.moveBy(position.x(), position.y())

        return graph_node

    def _drawConnection(self, parent: GraphNode, child: GraphNode):
        if parent.childrenLine is None:
            ConnectionMultiline(parent, child)
        else:
            parent.childrenLine.addChild(child)

    def _moveNodesBelow(self, node: Node):
        node_forest_root = self._forest.find_root(node)
        root_index = self._forest.roots.index(node_forest_root)
        for root in self._forest.roots[root_index+1:]:
            self._moveSubtreeBelow(root)

        ancestors = self._forest.get_path_to_root(node)
        for ancestor in ancestors:
            ancestor_index = ancestor.index_by_parent()
            ancestor_younger_siblings = ancestor.parent.successors[ancestor_index+1:]
            for ancestor_sibling in ancestor_younger_siblings:
                self._moveSubtreeBelow(ancestor_sibling)

            if len(ancestor_younger_siblings) > 0:
                top_moving_port = ancestor_younger_siblings[0].content.parentPort.portNumber
                ancestor_parent_multiline = ancestor.content.parentPort.multiline
                ancestor_parent_multiline.stretch(top_moving_port, GraphView.VERTICAL_STEP)

    def _moveNodesAbove(self, node: Node):
        siblings = self._forest.get_siblings_from(node)
        for sibling in siblings:
            self._moveSubtreeAbove(sibling)

        ancestors = self._forest.get_path_to_root(node)
        for ancestor in ancestors:
            ancestor_index = ancestor.index_by_parent()
            ancestor_younger_siblings = ancestor.parent.successors[ancestor_index+1:]
            for ancestor_sibling in ancestor_younger_siblings:
                self._moveSubtreeAbove(ancestor_sibling)

            if len(ancestor_younger_siblings) > 0:
                top_moving_port = ancestor_younger_siblings[0].content.parentPort.portNumber
                ancestor_parent_multiline = ancestor.content.parentPort.multiline
                ancestor_parent_multiline.stretch(top_moving_port, -GraphView.VERTICAL_STEP)

        node_forest_root = self._forest.find_root(node)
        root_index = self._forest.roots.index(node_forest_root)
        for root in self._forest.roots[root_index+1:]:
            self._moveSubtreeAbove(root)

    # TODO: Implement via ConnectionMultiline
    # TODO: Implement everywhere via moveBelowBy(step)
    def _moveSubtreeBelow(self, subroot: Node):
        graph_subroot = subroot.content
        graph_subroot.moveBy(0, GraphView.VERTICAL_STEP)
        if subroot.is_parent():
            graph_subroot.childrenLine.callForAllLines("moveBy", 0, GraphView.VERTICAL_STEP)
        for successor in subroot.successors:
            self._moveSubtreeBelow(successor)

    def _moveSubtreeAbove(self, subroot: Node):
        graph_subroot = subroot.content
        graph_subroot.moveBy(0, -GraphView.VERTICAL_STEP)
        if subroot.is_parent():
            graph_subroot.childrenLine.callForAllLines("moveBy", 0, -GraphView.VERTICAL_STEP)
        for successor in subroot.successors:
            self._moveSubtreeAbove(successor)

    def _calcNewRootPosition(self) -> QPointF:
        x = GraphView.HORIZONTAL_GAP
        layer = self._forest.calc_width() + 1
        y = GraphView.VERTICAL_GAP + (layer-1) * GraphView.VERTICAL_STEP
        return QPointF(x, y)
