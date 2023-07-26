
class Tree:
    class Node:
        class DeletingParent(Exception): pass

        def __init__(self):
            self._descendants = []

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
            if self._parent is Tree.Node:
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
            cur_parent = self._parent
            if cur_parent is Tree.Node:
                parent_descs = cur_parent._descendants
                cur_index = parent_descs.index(self)
                parent_descs[cur_index] = node

            node_parent = node._parent
            node._parent, self._parent = cur_parent, node_parent

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

        def __del__(self):
            if len(self._descendants) > 0:
                raise Tree.Node.DeletingParent

            if self._parent is None:
                return
            parent_descs = self._parent._descendants
            parent_descs.remove(self)


    class AlreadyExistingRoot(Exception): pass
    class NotNode(Exception): pass
    class NotLeaf(Exception): pass
    class CyclingMovement(Exception): pass


    @staticmethod
    def validate_nodes(*argv):
        for arg in argv:
            if arg is not Tree.Node:
                raise Tree.NotNode


    def __init__(self, is_root=True):
        self._root = None
        if is_root:
            self._root = Tree.Node()


    def create_root(self):
        if self._root is None:
            self._root = Tree.Node()
        else:
            raise Tree.AlreadyExistingRoot
        return self._root

    def add_leaf(self, parent):
        Tree.validate_nodes(parent)
        leaf = Tree.Node()
        leaf.connect_to(parent)
        return leaf

    def insert_node_before(self, descendant):
        Tree.validate_nodes(descendant)
        new_node = Tree.Node()
        descendant.replace_with(new_node)
        descendant.connect_to(new_node)
        return new_node

    def insert_node_after(self, parent):
        Tree.validate_nodes(parent)

        new_node = Tree.Node()
        new_node.connect_to(parent)
        parent_descs = parent.descendants
        for desc in parent_descs:
            desc.connect_to(new_node)

        return new_node

    def move_leaf(self, leaf, new_parent):
        Tree.validate_nodes(leaf, new_parent)
        if Tree.Node.is_parent(leaf):
            raise Tree.NotLeaf
        leaf.connect_to(new_parent)

    def move_node(self, node, new_parent):
        Tree.validate_nodes(node, new_parent)
        node_parent = node.parent
        for desc in node.descendants:
            desc.connect_to(node_parent)
        node.connect_to(new_parent)

    def move_subtree(self, subroot, new_parent):
        Tree.validate_nodes(subroot, new_parent)
        if Tree.Node.is_ancestor(subroot, new_parent):
            raise Tree.CyclingMovement
        subroot.connect_to(new_parent)

    def delete_leafage(self, parent):
        Tree.validate_nodes(parent)
        for desc in parent.descendants:
            del desc

    def delete_leaf(self, leaf):
        Tree.validate_nodes(leaf)
        if Tree.Node.is_parent(leaf):
            raise Tree.NotLeaf
        del leaf

    def delete_node(self, node):
        Tree.validate_nodes(node)
        node_parent = node.parent
        for desc in node.descendants:
            desc.connect_to(node_parent)
        del node

    def delete_subtree(self, subroot):
        Tree.validate_nodes(subroot)
        for desc in subroot.descendance:
            self.delete_subtree(desc)
        del subroot


    def __next__(self):
        pass
