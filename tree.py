
from __future__ import annotations


class Node:
    def __init__(self):
        self._parent = None
        self._successors = []
        self._content = None


    def connect_to(self, parent: Node):
        if self._parent is Node:
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
        if cur_parent is Node:
            parent_successors = cur_parent.successors
            cur_index = parent_successors.index(self)
            parent_successors[cur_index] = node

        node_parent = node._parent
        node._parent, self._parent = cur_parent, node_parent


    def is_root(self):
        return self._parent is None

    def is_parent(self):
        return len(self._successors) > 0

    def is_ancestor(self, second: Node):
        cur_parent = second._parent
        while cur_parent is not None:
            if cur_parent == self:
                return True
        return False


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
    class CyclingMovement(Exception): pass
    class AlienNode(Exception): pass


    def __init__(self, is_root=True):
        self._roots = []
        if is_root:
            self._roots.append(self._create_node())


    def create_root(self) -> _ForestNode:
        self._roots.append(self._create_node())
        return self._roots[-1]

    def add_leaf(self, parent: _ForestNode) -> _ForestNode:
        self._validate_nodes(parent)
        leaf = self._create_node()
        leaf.connect_to(parent)
        return leaf

    def insert_node_before(self, successor: _ForestNode) -> _ForestNode:
        self._validate_nodes(successor)
        new_node = self._create_node()
        successor.replace_with(new_node)
        successor.connect_to(new_node)
        return new_node

    def insert_node_after(self, parent: _ForestNode) -> _ForestNode:
        self._validate_nodes(parent)

        new_node = self._create_node()
        new_node.connect_to(parent)
        parent_successors = parent.successors
        for successor in parent_successors:
            successor.connect_to(new_node)

        return new_node

    def move_node(self, node: _ForestNode, new_parent: _ForestNode):
        self._validate_nodes(node, new_parent)
        node_parent = node.parent
        for successor in node.successors:
            successor.connect_to(node_parent)
        node.connect_to(new_parent)

    def move_subtree(self, subroot: _ForestNode, new_parent: _ForestNode):
        self._validate_nodes(subroot, new_parent)
        if subroot.is_ancestor(new_parent):
            raise Forest.CyclingMovement
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


    # Private part
    class _ForestNode(Node):
        def __init__(self, forest):
            super().__init__()
            self._forest = forest

        def set_forest_ref(self, new_forest_ref):
            self._forest = new_forest_ref

        def get_forest_ref(self):
            return self._forest

    def _create_node(self) -> _ForestNode:
        return Forest._ForestNode(self)

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
            if arg is not Node:
                raise Forest.NotNode
            if arg.get_forest_ref() != self:
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
