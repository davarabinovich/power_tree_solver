
from __future__ import annotations

# TODO: Write disclamer about order of successors - this module is implemented with ordered successors and tested with
#       assumption of that they're ordered, but doesn't have any methods to change this order, and the developer meant
#       a usual tree with unordered node's leafage.

# TODO: Rework to _successors be a set
# TODO: Implement convenient tools for tree structure visualization
class Node:
    class ClosingTransition(Exception): pass


    def __init__(self, content=None):
        self._parent = None
        self._successors = []
        self._content = content


    @staticmethod
    def build_tree(nodes_list: list, parent=None):
        root = Node()
        root.content = nodes_list[0]
        nodes_list = nodes_list[1:]

        if parent is not None:
            parent.successors.append(root)
            root.parent = parent

        for subtree in nodes_list:
            if type(subtree) == list:
                Node.build_tree(subtree, root)
            else:
                successor = Node()
                successor.content = subtree
                root.successors.append(successor)
                successor.parent = root

        return root


    def connect_to(self, parent: Node):
        if self.is_ancestor(parent):
            raise Node.ClosingTransition

        if isinstance(self._parent, Node):
            self._parent.successors.remove(self)
        self._parent = parent
        parent._successors.append(self)

    def disconnect(self):
        if self._parent is None:
            return
        self._parent.successors.remove(self)
        self._parent = None

    def replace_with(self, node: Node):
        cur_parent = self._parent
        if isinstance(cur_parent, Node):
            parent_successors = cur_parent.successors
            cur_index = parent_successors.index(self)
            parent_successors[cur_index] = node

        node_parent = node.parent
        if isinstance(node_parent, Node):
            parent_successors = node_parent.successors
            parent_successors.remove(node)

        node.parent = cur_parent
        self._parent = None

    def swap_with(self, node: Node):
        if self.is_ancestor(node):
            raise Node.ClosingTransition
        if node.is_ancestor(self):
            raise Node.ClosingTransition

        cur_parent = self._parent
        if isinstance(cur_parent, Node):
            parent_successors = cur_parent.successors
            cur_index = parent_successors.index(self)
            parent_successors[cur_index] = node

        node_parent = node.parent
        if isinstance(node_parent, Node):
            parent_successors = node_parent.successors
            cur_index = parent_successors.index(node)
            parent_successors[cur_index] = self

        node.parent = cur_parent
        self._parent = node_parent


    def is_root(self):
        return self._parent is None

    def is_successor(self):
        return self._parent is not None

    def is_parent(self):
        return len(self._successors) > 0

    def is_ancestor(self, second: Node):
        cur_parent = second._parent
        while isinstance(cur_parent, Node):
            if cur_parent == self:
                return True
            cur_parent = cur_parent._parent
        return False


    def __eq__(self, other: Node):
        if self.content != other.content:
            return False
        if len(self.successors) != len(other.successors):
            return False

        for index in range(len(self.successors)):
            if not self.successors[index].__eq__(other.successors[index]):
                return False

        return True

    @property
    def content(self):
        return self._content
    @content.setter
    def content(self, value):
        self._content = value

    @property
    def parent(self):
        return self._parent
    @parent.setter
    def parent(self, value):
        self._parent = value

    @property
    def successors(self):
        return self._successors
    @successors.setter
    def successors(self, value):
        self._successors = value


class Forest:
    # Public interface
    class NotNode(Exception): pass
    class NotLeaf(Exception): pass
    class NotSuccessor(Exception):pass
    class AlienNode(Exception): pass


    def __init__(self, root=None):
        if root is None:
            self._roots = []
        else:
            self._roots.append(self._create_node())


    @staticmethod
    def build_forest(*argv: list):
        forest = Forest()
        for tree in argv:
            root = Forest._build_tree(tree, forest)
            forest._roots.append(root)
        return forest


    # TODO: Optimize all modificating functions with for loops
    def create_root(self, content=None) -> _ForestNode:
        self._roots.append(self._create_node(content))
        return self._roots[-1]

    def add_leaf(self, parent: _ForestNode, content=None) -> _ForestNode:
        self._validate_nodes(parent)
        leaf = self._create_node(content)
        leaf.connect_to(parent)
        return leaf

    def insert_node_before(self, new_successor: _ForestNode, content=None) -> _ForestNode:
        self._validate_nodes(new_successor)

        new_node = self._create_node(content)
        if new_successor.is_root():
            index = self._roots.index(new_successor)
            self._roots[index] = new_node

        new_successor.replace_with(new_node)
        new_successor.connect_to(new_node)
        return new_node

    def insert_node_after(self, new_parent: _ForestNode, content=None) -> _ForestNode:
        self._validate_nodes(new_parent)
        new_node = self._create_node(content)

        temp_parent_successors = []
        for successor in new_parent.successors:
            temp_parent_successors.append(successor)
        for successor in temp_parent_successors:
            successor.connect_to(new_node)

        new_node.connect_to(new_parent)
        return new_node

    def move_node(self, node: _ForestNode, new_parent: _ForestNode):
        self._validate_nodes(node, new_parent)
        temp_node_successors = []
        for successor in node.successors:
            temp_node_successors.append(successor)

        if node.is_successor():
            for successor in temp_node_successors:
                node_parent = node.parent
                successor.connect_to(node_parent)
        else:
            self._roots.remove(node)
            for successor in temp_node_successors:
                self._make_root(successor)

        node.connect_to(new_parent)

    def move_subtree(self, subroot: _ForestNode, new_parent: _ForestNode):
        self._validate_nodes(subroot, new_parent)
        subroot.connect_to(new_parent)

    def free_node(self, node: _ForestNode):
        self._validate_nodes(node)
        node_parent = node.parent
        for successor in node.successors:
            successor.connect_to(node_parent)
        self._make_root(node)

    def free_subtree(self, subroot: _ForestNode):
        self._validate_nodes(subroot)
        self._make_root(subroot)

    def delete_leafage(self, parent: _ForestNode):
        self._validate_nodes(parent)
        for successor in parent.successors:
            self._delete_subtree(successor)
            # TODO : Solve warning
            # class A:
            #     def __init__(self):
            #         pass
            #
            #     def __del__(self):
            #         print("Deleted")
            #
            # list_a = [A(), A(), A()]
            # another_list_a = [A(), A(), A()]
            # list_a.clear()
            #
            # output:
            # Deleted
            # Deleted
            # Deleted
            # Deleted
            # Deleted
            # Deleted
            #
            # Why six times?

    def delete_leaf(self, leaf: _ForestNode):
        self._validate_nodes(leaf)
        if leaf.is_parent():
            raise Forest.NotLeaf
        self._delete_node(leaf)

    def cut_node(self, node: _ForestNode):
        self._validate_nodes(node)
        if node.is_root():
            raise Forest.NotSuccessor

        node_parent = node.parent
        for successor in node.successors:
            successor.connect_to(node_parent)
        self._delete_node(node)

    def delete_subtree(self, subroot: _ForestNode):
        self._validate_nodes(subroot)

        for successor in subroot.successors:
            self.delete_subtree(successor)
        if subroot.is_root():
            self._roots.remove(subroot)
        self._delete_subtree(subroot)


    def __iter__(self):
        self._cur_indices = [0]
        self._cur_node = self._roots[0]
        return self

    # TODO: Traverse by subroot with syntax identical to traverse by the whole tree
    def __next__(self):
        if self._cur_node.is_parent():
            self._cur_indices.append(0)
            self._cur_node = self._cur_node.successors[0]
            return self._cur_node

        self._cur_indices[-1] += 1
        if len(self._cur_node.parent.successors)-1 >= self._cur_indices[-1]:
            self._cur_node = self._cur_node.parent.successors[self._cur_indices[-1]]
            return self._cur_node

        while len(self._cur_node.parent.successors)-1 == self._cur_indices[-1]:
            self._cur_indices.pop(-1)
            self._cur_node = self._cur_node.parent

            if self._cur_node.is_root():
                self._cur_indices[-1] += 1
                if len(self._roots) == self._cur_indices[-1]:
                    raise StopIteration
                return self._roots[self._cur_indices[0]]

        self._cur_indices[-1] += 1
        self._cur_node = self._cur_node.parent.successors[self._cur_indices[-1]]
        return self._cur_node

    def __eq__(self, other: Forest):
        if len(self._roots) != len(other._roots):
            return False

        for index in range(len(self._roots)):
            if not self._roots[index].__eq__(other._roots[index]):
                return False
        return True


    @property
    def roots(self):
        return self._roots


    # Private part
    class _ForestNode(Node):
        def __init__(self, forest: Forest, content=None):
            super().__init__(content)
            self._forest = forest

        def set_forest_ref(self, new_forest_ref):
            self._forest = new_forest_ref

        def get_forest_ref(self):
            return self._forest

    # TODO: Combine with Node.build_tree
    @staticmethod
    def _build_tree(nodes_list: list, forest: Forest, parent=None):
        root = Forest._ForestNode(forest)
        root.content = nodes_list[0]
        nodes_list = nodes_list[1:]

        if parent is not None:
            parent.successors.append(root)
            root.parent = parent

        for subtree in nodes_list:
            if type(subtree) == list:
                Forest._build_tree(subtree, forest, root)
            else:
                successor = Forest._ForestNode(forest)
                successor.content = subtree
                root.successors.append(successor)
                successor.parent = root

        return root

    def _create_node(self, content=None) -> _ForestNode:
        return Forest._ForestNode(self, content)

    def _delete_node(self, node: _ForestNode):
        node.set_forest_ref(None)
        node.disconnect()

    def _delete_subtree(self, subroot: _ForestNode):
        def clear_forest_refs_recursively(subroot: Forest._ForestNode):
            for successor in subroot.successors:
                clear_forest_refs_recursively(successor)
            subroot.set_forest_ref(None)

        subroot.disconnect()
        clear_forest_refs_recursively(subroot)


    def _make_root(self, node: _ForestNode):
        node.disconnect()
        self._roots.append(node)

    def _validate_nodes(self, *argv):
        for arg in argv:
            if type(arg) != Forest._ForestNode:
                raise Forest.NotNode
            if id(arg.get_forest_ref()) != id(self):
                raise Forest.AlienNode


class Tree(Forest):
    class AlreadyExistingRoot(Exception): pass

    def __init__(self):
        super().__init__()
        self._roots = (self._create_node(),)

    @staticmethod
    def create(node: Node) -> Tree:
        # TODO : Copy successors or not
        pass

    def create_root(self):
        raise Tree.AlreadyExistingRoot

    def free_node(self, node: Forest._ForestNode) -> Tree:
        # TODO: To implement
        pass

    def free_subtree(self, subroot: Forest._ForestNode) -> Tree:
        # TODO: To implement
        pass

    def _make_root(self, node: Forest._ForestNode):
        raise Tree.AlreadyExistingRoot
