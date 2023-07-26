
from typing import NewType


class Forest:
    class Node:
        class DeletingParent(Exception): pass
        class IncompatibleNodes(Exception): pass

        def __init__(self, forest=None):
            self._descendants = []
            self._forest = forest
            self._content = None

        @staticmethod
        def is_root(node):
            return node._parent == None

        @staticmethod
        def is_parent(node):
            return len(node._descendants) > 0

        @staticmethod
        def is_ancestor(first, second):
            cur_parent = second._parent
            while (cur_parent is not None):
                if cur_parent == first:
                    return True
            return False

        def connect_to(self, parent):
            if self._forest != parent._forest:
                raise Forest.Node.IncompatibleNodes

            if self._parent is Forest.Node:
                self.disconnect()
            self._parent = parent
            parent._descendants.append(self)

        def disconnect(self):
            if self._parent is None:
                return
            parent_descs = self._parent._descendants
            parent_descs.remove(self)
            self._parent = None

        def replace_with(self, node):
            if self._forest != node._forest:
                raise Forest.Node.IncompatibleNodes

            cur_parent = self._parent
            if cur_parent is Forest.Node:
                parent_descs = cur_parent._descendants
                cur_index = parent_descs.index(self)
                parent_descs[cur_index] = node

            node_parent = node._parent
            node._parent, self._parent = cur_parent, node_parent

        @property
        def content(self):
            return self._content
        @content.setter
        def content(self, value):
            self._content = value

        @property
        def descendants(self):
            return self._descendants
        @descendants.setter
        def descendants(self, value):
            self._descendants = value

        @property
        def parent(self):
            return self._parent
        @parent.setter
        def parent(self, value):
            self._parent = value

        @property
        def forest(self):
            return self._forest

        def __del__(self):
            if len(self._descendants) > 0:
                raise Forest.Node.DeletingParent

            if self._parent is None:
                return
            parent_descs = self._parent._descendants
            parent_descs.remove(self)
    TreeNode = NewType('TreeNode', Node)


    class NotNode(Exception): pass
    class NotLeaf(Exception): pass
    class CyclingMovement(Exception): pass


    @staticmethod
    def validate_nodes(*argv):
        for arg in argv:
            if arg is not Forest.Node:
                raise Forest.NotNode


    def __init__(self, is_root=True):
        self._roots = []
        if is_root:
            self._roots.append(Forest.Node())


    def create_root(self):
        self._roots.append(Forest.Node())
        return self._roots

    def add_leaf(self, parent : TreeNode):
        Forest.validate_nodes(parent)
        leaf = self._create_node()
        leaf.connect_to(parent)
        return leaf

    def insert_node_before(self, descendant : TreeNode):
        Forest.validate_nodes(descendant)
        new_node = self._create_node()
        descendant.replace_with(new_node)
        descendant.connect_to(new_node)
        return new_node

    def insert_node_after(self, parent : TreeNode):
        Forest.validate_nodes(parent)

        new_node = self._create_node()
        new_node.connect_to(parent)
        parent_descs = parent.descendants
        for desc in parent_descs:
            desc.connect_to(new_node)

        return new_node

    def move_leaf(self, leaf : TreeNode, new_parent : TreeNode):
        Forest.validate_nodes(leaf, new_parent)
        if Forest.Node.is_parent(leaf):
            raise Forest.NotLeaf
        leaf.connect_to(new_parent)

    def move_node(self, node : TreeNode, new_parent : TreeNode):
        Forest.validate_nodes(node, new_parent)
        node_parent = node.parent
        for desc in node.descendants:
            desc.connect_to(node_parent)
        node.connect_to(new_parent)

    def move_subtree(self, subroot : TreeNode, new_parent : TreeNode):
        Forest.validate_nodes(subroot, new_parent)
        if Forest.Node.is_ancestor(subroot, new_parent):
            raise Forest.CyclingMovement
        subroot.connect_to(new_parent)

    def delete_leafage(self, parent : TreeNode):
        Forest.validate_nodes(parent)
        for desc in parent.descendants:
            del desc

    def delete_leaf(self, leaf : TreeNode):
        Forest.validate_nodes(leaf)
        if Forest.Node.is_parent(leaf):
            raise Forest.NotLeaf
        del leaf

    def delete_node(self, node : TreeNode):
        Forest.validate_nodes(node)
        node_parent = node.parent
        for desc in node.descendants:
            desc.connect_to(node_parent)
        del node

    def delete_subtree(self, subroot : TreeNode):
        Forest.validate_nodes(subroot)
        for desc in subroot.descendants:
            self.delete_subtree(desc)
        del subroot

    def get_node_content(self, node):
        return node.content

    def set_node_content(self, ):

    def _create_node(self) -> TreeNode:
        return Forest.Node(self)


    def __iter__(self):
        self._cur_indices = [0]
        self._cur_node = self._roots[0]
        return self

    def __next__(self):
        if Forest.Node.is_parent(self._cur_node):
            self._cur_indices.append(0)
            self._cur_node = self._cur_node.descendants[0]
            return self._cur_node

        self._cur_indices[-1] += 1
        if len(self._cur_node.parent.descendants)-1 >= self._cur_indices[-1]:
            self._cur_node = self._cur_node.parent.descendants[self._cur_indices[-1]]
            return self._cur_node

        while len(self._cur_node.parent.descendants)-1 == self._cur_indices[-1]:
            self._cur_indices.pop(-1)
            self._cur_node = self._cur_node.parent

            if (Forest.Node.is_root(self._cur_node)):
                self._cur_indices[-1] += 1
                if len(self._roots) == self._cur_indices[-1]:
                    raise StopIteration
                return self._roots[self._cur_indices[0]]

        self._cur_indices[-1] += 1
        self._cur_node = self._cur_node.parent.descendants[self._cur_indices[-1]]
        return self._cur_node
