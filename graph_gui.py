
# Plan of reworking:
# To try:
#     - manual control of scene rect
#     - use different view updating policy (method, see GraphicsView reference, BSP tree)

from enum import Enum
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


    class DeletingParentAsLeaf(Exception): pass


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

    def deleteLeaf(self, graph_node: GraphNode):
        forest_node: Forest.ForestNode = graph_node.data(GraphView._FOREST_NODE_DATA_KEY)
        if forest_node.is_parent():
            raise GraphView.DeletingParentAsLeaf

        if forest_node.is_root():
            is_moving_above_needed = True
        elif len(forest_node.parent.successors) > 1:
            is_moving_above_needed = True
        else:
            is_moving_above_needed = False

        if is_moving_above_needed:
            self._moveNodesAbove(forest_node)

        if forest_node.is_successor():
            graph_node.parentPort.multiline.deleteChild(graph_node.parentPort.portNumber)
        self._forest.delete_leaf(forest_node)
        self._scene.removeItem(graph_node)

    def deleteParent(self, graph_node: GraphNode, new_parent: GraphNode=None):
        forest_node: Forest.ForestNode = graph_node.data(GraphView._FOREST_NODE_DATA_KEY)

        if new_parent is None:
            furthest_leaf, subtree_width = self._forest.find_furthest_leaf_with_distance(forest_node)
            if forest_node.is_root():
                distance = subtree_width + 1
            elif len(forest_node.parent.successors) == 1:
                distance = subtree_width
            else:
                distance = subtree_width + 1

            for i in range(distance):
                self._moveNodesAbove(furthest_leaf)
            self._removeSubtree(forest_node)
            self._forest.delete_subtree(forest_node)

        elif new_parent == forest_node.parent.content:
            items = self._scene.items()
            children = forest_node.successors
            for child in children:
                self._moveSubtreeLeft(child)

            items = self._scene.items()
            parent_multiline = new_parent.childrenLine
            parent_multiline.deleteChild(graph_node.parentPort.portNumber)
            items = self._scene.items()

            if len(parent_multiline._children_ports) > 0:
                for index in reversed(range(len(children))):
                    graph_node.childrenLine.deleteChild(index+1)
                for index in range(len(children)):
                    parent_multiline.insertChild(children[index].content, graph_node.parentPort.portNumber+index)
            else:
                for index in reversed(range(len(children))):
                    graph_node.childrenLine.deleteChild(index+1)

                new_multiline = ConnectionMultiline(new_parent, children[0].content)
                for child in children[1:]:
                    new_multiline.addChild(child.content)

            items = self._scene.items()
            self._forest.cut_node(forest_node, is_needed_to_replace_node_with_successors=True)
            self._scene.removeItem(graph_node)

            items = self._scene.items()
            print('')

        else:
            # Ensure, that it's not closing movement
            new_parent_forest_node: Node = new_parent.data(GraphView._FOREST_NODE_DATA_KEY)
            if forest_node.is_ancestor(new_parent_forest_node):
                # TODO: Handle this case properly
                return

            delta_x, delta_y = self._forest.calc_distance(forest_node, new_parent_forest_node)
            children = forest_node.successors

            top_moving_node = self._forest.get_next_sibling(new_parent_forest_node)
            while top_moving_node is None:
                top_moving_node = self._forest.get_next_sibling(new_parent_forest_node.parent)

            for i in range(len(children)):
                self._moveNodesBelow(GraphView.VERTICAL_STEP)
            for child in children:
                self._moveSubtreeLeft(child, delta_x * GraphView.HORIZONTAL_STEP)
                self._moveSubtreeAbove(child. delta_y * GraphView.VERTICAL_STEP)

            parent_multiline = new_parent.childrenLine
            parent_multiline.deleteChild(graph_node.parentPort.portNumber)

            if len(parent_multiline._children_ports) > 0:
                for index in reversed(range(len(children))):
                    graph_node.childrenLine.deleteChild(index + 1)
                for index in range(len(children)):
                    parent_multiline.addChild(children[index].content)
            else:
                for index in reversed(range(len(children))):
                    graph_node.childrenLine.deleteChild(index + 1)

                new_multiline = ConnectionMultiline(new_parent, children[0].content)
                for child in children[1:]:
                    new_multiline.addChild(child.content)

            self._forest.move_subtree(forest_node, new_parent_forest_node)
            self._forest.cut_node(forest_node, is_needed_to_replace_node_with_successors=True)
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
            delta_y = (parent_width + 1) * GraphView.VERTICAL_STEP
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
            multiline = ConnectionMultiline(parent, child)
        else:
            parent.childrenLine.addChild(child)

    def _moveNodesBelow(self, node: Node, delta_y=VERTICAL_STEP):
        node_forest_root = self._forest.find_root(node)
        root_index = self._forest.roots.index(node_forest_root)
        for root in self._forest.roots[root_index+1:]:
            self._moveSubtreeBelow(root, delta_y)

        ancestors = self._forest.get_path_to_root(node)
        for ancestor in ancestors:
            ancestor_index = ancestor.index_by_parent()
            ancestor_younger_siblings = ancestor.parent.successors[ancestor_index+1:]
            for ancestor_sibling in ancestor_younger_siblings:
                self._moveSubtreeBelow(ancestor_sibling, delta_y)

            if len(ancestor_younger_siblings) > 0:
                top_moving_port = ancestor_younger_siblings[0].content.parentPort.portNumber
                ancestor_parent_multiline = ancestor.content.parentPort.multiline
                ancestor_parent_multiline.stretch(top_moving_port, delta_y)

    def _moveNodesAbove(self, node: Node):
        siblings = self._forest.get_siblings_from(node)[1:]
        for sibling in siblings:
            self._moveSubtreeAbove(sibling)
        if len(siblings) > 0:
            parent_multiline = node.content.parentPort.multiline
            parent_multiline.stretch(siblings[0].content.parentPort.portNumber, -GraphView.VERTICAL_STEP)

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
    def _moveSubtreeBelow(self, subroot: Node, delta_y=VERTICAL_STEP):
        graph_subroot = subroot.content
        graph_subroot.moveBy(0, delta_y)
        if subroot.is_parent():
            graph_subroot.childrenLine.callForAllLines("moveBy", 0, delta_y)
        for successor in subroot.successors:
            self._moveSubtreeBelow(successor)

    def _moveSubtreeAbove(self, subroot: Node):
        graph_subroot = subroot.content
        graph_subroot.moveBy(0, -GraphView.VERTICAL_STEP)
        if subroot.is_parent():
            graph_subroot.childrenLine.callForAllLines("moveBy", 0, -GraphView.VERTICAL_STEP)
        for successor in subroot.successors:
            self._moveSubtreeAbove(successor)

    def _moveSubtreeLeft(self, subroot: Forest.ForestNode, delta_x=HORIZONTAL_STEP):
        graph_subroot = subroot.content
        graph_subroot.moveBy(-delta_x, 0)
        if subroot.is_parent():
            graph_subroot.childrenLine.moveBy(-delta_x, 0)
        for successor in subroot.successors:
            self._moveSubtreeLeft(successor)

    def _removeSubtree(self, subroot: Forest.ForestNode):
        graph_node = subroot.content
        if subroot.is_successor():
            graph_node.parentPort.multiline.deleteChild(graph_node.parentPort.portNumber)
        self._scene.removeItem(graph_node)
        for child in reversed(subroot.successors):
            self._removeSubtree(child)

    def _calcNewRootPosition(self) -> QPointF:
        x = GraphView.HORIZONTAL_GAP
        layer = self._forest.calc_width() + 1
        y = GraphView.VERTICAL_GAP + (layer-1) * GraphView.VERTICAL_STEP
        return QPointF(x, y)
