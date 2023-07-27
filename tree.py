
from __future__ import annotations


class Node:
    class DeletingParent(Exception): pass


    def __init__(self):
        self._parent = None
        self._successors = []
        self._content = None


    def connect_to(self, parent : Node):
        if self._parent is Node:
            self._parent.successors.remove(self)
        self._parent = parent
        parent._successors.append(self)

    def disconnect(self):
        if self._parent is None:
            return
        self._parent.successors.remove(self)
        self._parent = None

    def replace_with(self, node : Node):
        cur_parent = self._parent
        if cur_parent is Node:
            parent_descs = cur_parent._successors
            cur_index = parent_descs.index(self)
            parent_descs[cur_index] = node

        node_parent = node._parent
        node._parent, self._parent = cur_parent, node_parent


    def is_root(self):
        return self._parent == None

    def is_parent(self):
        return len(self._successors) > 0

    def is_ancestor(self, second : Node):
        cur_parent = second._parent
        while cur_parent is not None:
            if cur_parent == self:
                return True
        return False


    def __del__(self):
        if len(self._successors) > 0:
            raise Node.DeletingParent

        if self._parent is None:
            return
        self._parent._successors.remove(self)


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
    class NotSuccessor(Exception) :pass
    class CyclingMovement(Exception): pass
    class AlienNode(Exception): pass


    def __init__(self, is_root=True):
        self._roots = []
        if is_root:
            self._roots.append(self._create_node())


    def create_root(self) -> ForestNode:
        self._roots.append(self._create_node())
        return self._roots[-1]

    def add_leaf(self, parent : ForestNode) -> ForestNode:
        self._validate_nodes(parent)
        leaf = self._create_node()
        leaf.connect_to(parent)
        return leaf

    def insert_node_before(self, successor : ForestNode) -> ForestNode:
        self._validate_nodes(successor)
        new_node = self._create_node()
        successor.replace_with(new_node)
        successor.connect_to(new_node)
        return new_node

    def insert_node_after(self, parent : ForestNode) -> ForestNode:
        self._validate_nodes(parent)

        new_node = self._create_node()
        new_node.connect_to(parent)
        parent_descs = parent._successors
        for desc in parent_descs:
            desc.connect_to(new_node)

        return new_node

    def move_node(self, node : ForestNode, new_parent : ForestNode):
        self._validate_nodes(node, new_parent)
        node_parent = node._parent
        for desc in node._successors:
            desc.connect_to(node_parent)
        node.connect_to(new_parent)

    def move_subtree(self, subroot : ForestNode, new_parent : ForestNode):
        self._validate_nodes(subroot, new_parent)
        if subroot.is_ancestor(new_parent):
            raise Forest.CyclingMovement
        subroot.connect_to(new_parent)

    def free_node(self, node : ForestNode):
        self._validate_nodes(node)
        node_parent = node._parent
        for desc in node._successors:
            desc.connect_to(node_parent)
        self._make_root(node)

    def free_subtree(self, subroot : ForestNode):
        self._validate_nodes(subroot)
        self._make_root(subroot)

    def delete_leafage(self, parent : ForestNode):
        self._validate_nodes(parent)
        for desc in parent._successors:
            del desc

    def delete_leaf(self, leaf : ForestNode):
        self._validate_nodes(leaf)
        if leaf.is_parent():
            raise Forest.NotLeaf
        del leaf

    def cut_node(self, node : ForestNode):
        self._validate_nodes(node)
        if node.is_root():
            raise Forest.NotSuccessor

        node_parent = node._parent
        for desc in node._successors:
            desc.connect_to(node_parent)
        del node

    def delete_subtree(self, subroot : ForestNode):
        self._validate_nodes(subroot)

        for desc in subroot._successors:
            self.delete_subtree(desc)
        if subroot.is_root():
            self._roots.remove(subroot)
        del subroot


    def __iter__(self):
        self._cur_indices = [0]
        self._cur_node = self._roots[0]
        return self

    # TODO: Traverse by subroot with syntax indentical to traverse by the whole tree
    def __next__(self):
        if self._cur_node.is_parent():
            self._cur_indices.append(0)
            self._cur_node = self._cur_node._successors[0]
            return self._cur_node

        self._cur_indices[-1] += 1
        if len(self._cur_node._parent._successors)-1 >= self._cur_indices[-1]:
            self._cur_node = self._cur_node._parent._successors[self._cur_indices[-1]]
            return self._cur_node

        while len(self._cur_node.parent.descendants)-1 == self._cur_indices[-1]:
            self._cur_indices.pop(-1)
            self._cur_node = self._cur_node.parent

            if self._cur_node.is_root():
                self._cur_indices[-1] += 1
                if len(self._roots) == self._cur_indices[-1]:
                    raise StopIteration
                return self._roots[self._cur_indices[0]]

        self._cur_indices[-1] += 1
        self._cur_node = self._cur_node.parent.descendants[self._cur_indices[-1]]
        return self._cur_node


    # Private part
    class ForestNode(Node):
        def __init__(self, forest):
            super().__init__()
            self._forest = forest

        def set_forest_ref(self, new_forest_ref):
            self._forest = new_forest_ref

        def get_forest_ref(self):
            return self._forest

    def _create_node(self) -> ForestNode:
        return Forest.ForestNode(self)

    def _make_root(self, node : ForestNode):
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
    def create(node : Node) -> Tree:
        # TODO : Copy successors or not
        pass

    def create_root(self):
        raise Tree.AlreadyExistingRoot

    def free_node(self, node : Forest.ForestNode) -> Tree:
        # TODO: To implement
        pass

    def free_subtree(self, subroot : Forest.ForestNode) -> Tree:
        # TODO: To implement
        pass

    def _make_root(self, node : Forest.ForestNode):
        raise Tree.AlreadyExistingRoot
