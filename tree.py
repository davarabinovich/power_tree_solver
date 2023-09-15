
from __future__ import annotations

# TODO: Write disclamer about order of successors - this module is implemented with ordered successors and tested with
#       assumption of that they're ordered, but doesn't have any methods to change this order, and the developer meant
#       a usual tree with unordered node's leafage.

# TODO: Rework to _successors be a set
# TODO: Implement convenient tools for tree structure visualization
class Node:
    # Public interface
    class ClosingTransition(Exception): pass


    def __init__(self, content=None):
        self._parent: Node | None = None
        self._successors: list[Node] = []
        self._content = content

        self._cur_indices = None
        self._cur_node = None
        self._is_first_iteration = False


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
        if isinstance(parent, Node):
            if self.is_ancestor(parent):
                raise Node.ClosingTransition

        if isinstance(self._parent, Node):
            self._parent.successors.remove(self)
        self._parent = parent
        if isinstance(parent, Node):
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


    def __iter__(self):
        self._cur_indices = [0]
        self._cur_node = self
        self._is_first_iteration = True
        return self

    def __next__(self):
        result = self._cur_node

        if self._is_on_itself():
            if self._is_first_iteration:
                self._is_first_iteration = False
                if self.is_leaf():
                    return result
            else:
                raise StopIteration

        if self._cur_node.is_parent():
            self._cur_indices.append(0)
            self._cur_node = self._cur_node.successors[0]
        elif not self._is_last_sibling():
            self._go_to_next_sibling()
        else:
            while self._is_last_sibling():
                self._cur_indices.pop(-1)
                self._cur_node = self._cur_node.parent
                if self._is_on_itself():
                    return result
            self._go_to_next_sibling()

        return result

    def calc_subtree_width(self):
        width = 0
        if len(self._successors) > 0:
            for successor in self._successors:
                width += successor.calc_subtree_width()
        else:
             width = 1

        return width

    # TODO: it is used in only graph_gui. Need to be used in Tree module.
    def index_by_parent(self):
        parent = self._parent
        index = parent.successors.index(self)
        return index

    def is_root(self):
        return self._parent is None

    def is_successor(self):
        return self._parent is not None

    def is_parent(self):
        return len(self._successors) > 0

    # TODO: Test it
    def is_leaf(self):
        return len(self._successors) == 0

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


    # Private part
    def _is_on_itself(self):
        return id(self._cur_node) == id(self)

    def _is_last_sibling(self):
        return len(self._cur_node.parent.successors) - 1 == self._cur_indices[-1]

    def _go_to_next_sibling(self):
        self._cur_indices[-1] += 1
        self._cur_node = self._cur_node.parent.successors[self._cur_indices[-1]]


# TODO: Try implementation with fictive root of roots to simplify modification method's code
class Forest:
    # Public interface
    class ForestNode(Node):
        def __init__(self, forest: Forest, content=None):
            super().__init__(content)
            self._forest = forest

        def set_forest_ref(self, new_forest_ref):
            self._forest = new_forest_ref

        def get_forest_ref(self):
            return self._forest


    class NotNode(Exception): pass
    class NotLeaf(Exception): pass
    class AlienNode(Exception): pass


    def __init__(self):
        self._roots = []
        self._cur_node = None
        self._cur_tree = -1


    @staticmethod
    def build_forest(*argv: list):
        forest = Forest()
        for tree in argv:
            root = Forest._build_tree(tree, forest)
            forest._roots.append(root)
        return forest


    # TODO: Optimize all modificating functions with for loops
    def create_root(self, content=None) -> ForestNode:
        self._roots.append(self._create_node(content))
        return self._roots[-1]

    def add_leaf(self, parent: ForestNode, content=None) -> ForestNode:
        self._validate_nodes(parent)
        leaf = self._create_node(content)
        leaf.connect_to(parent)
        return leaf

    def insert_node_before(self, new_successor: ForestNode, content=None) -> ForestNode:
        self._validate_nodes(new_successor)

        new_node = self._create_node(content)
        if new_successor.is_root():
            index = self._roots.index(new_successor)
            self._roots[index] = new_node

        new_successor.replace_with(new_node)
        new_successor.connect_to(new_node)
        return new_node

    def insert_node_after(self, new_parent: ForestNode, content=None) -> ForestNode:
        self._validate_nodes(new_parent)
        new_node = self._create_node(content)

        temp_parent_successors = []
        for successor in new_parent.successors:
            temp_parent_successors.append(successor)
        for successor in temp_parent_successors:
            successor.connect_to(new_node)

        new_node.connect_to(new_parent)
        return new_node

    def move_node(self, node: ForestNode, new_parent: ForestNode):
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

    def move_subtree(self, subroot: ForestNode, new_parent: ForestNode):
        self._validate_nodes(subroot, new_parent)
        is_root = subroot.is_root()
        subroot.connect_to(new_parent)
        if is_root:
            self._roots.remove(subroot)

    def free_leafage(self, parent: ForestNode):
        self._validate_nodes(parent)
        temp_node_successors = []
        for successor in parent.successors:
            temp_node_successors.append(successor)
        for successor in temp_node_successors:
            self._make_root(successor)

    def free_leaf(self, leaf: ForestNode):
        self._validate_nodes(leaf)
        if leaf.is_parent():
            raise Forest.NotLeaf
        if leaf.is_successor():
            self._make_root(leaf)

    def free_node(self, node: ForestNode):
        self._validate_nodes(node)
        node_parent = node.parent

        temp_node_successors = []
        for successor in node.successors:
            temp_node_successors.append(successor)
        for successor in temp_node_successors:
            successor.connect_to(node_parent)

        if node.is_root():
            for successor in temp_node_successors:
                self._make_root(successor)
        else:
            self._make_root(node)

    def free_subtree(self, subroot: ForestNode):
        self._validate_nodes(subroot)
        if subroot.is_successor():
            self._make_root(subroot)

    def delete_leafage(self, parent: ForestNode):
        self._validate_nodes(parent)
        temp_node_successors = []
        for successor in parent.successors:
            temp_node_successors.append(successor)
        for successor in temp_node_successors:
            successor.disconnect()
            self._remove_subtree_from_forest(successor)

    def delete_leaf(self, leaf: ForestNode):
        self._validate_nodes(leaf)
        if leaf.is_parent():
            raise Forest.NotLeaf
        if leaf.is_root():
            self._roots.remove(leaf)
        self._delete_node(leaf)

    def cut_node(self, node: ForestNode, is_needed_to_replace_node_with_successors=False):
        self._validate_nodes(node)
        if node.is_root():
            self._roots.remove(node)

        temp_node_successors = []
        for successor in node.successors:
            temp_node_successors.append(successor)

        node_parent = node.parent
        if is_needed_to_replace_node_with_successors:
            node_index = node_parent.successors.index(node)
            next_siblings = []
            for sibling in reversed(node_parent.successors[node_index+1:]):
                sibling.disconnect()
                next_siblings.append(sibling)
            for successor in temp_node_successors:
                successor.connect_to(node_parent)
            for sibling in next_siblings:
                sibling.connect_to(node_parent)
        else:
            for successor in temp_node_successors:
                successor.connect_to(node_parent)

        if node.is_root():
            for successor in temp_node_successors:
                self._roots.append(successor)

        self._delete_node(node)

    def delete_subtree(self, subroot: ForestNode):
        self._validate_nodes(subroot)
        if subroot.is_root():
            self._roots.remove(subroot)
        subroot.disconnect()
        self._remove_subtree_from_forest(subroot)


    def __iter__(self):
        if len(self._roots) > 0:
            self._roots[0].__iter__()
            self._cur_node = self._roots[0]
            self._cur_tree = 0
        return self

    def __next__(self):
        if self._cur_node is None:
            raise StopIteration

        try:
            self._cur_node = self._roots[self._cur_tree].__next__()
        except StopIteration:
            self._cur_tree += 1
            if len(self._roots) == self._cur_tree:
                raise StopIteration
            else:
                self._roots[self._cur_tree].__iter__()
                self._cur_node = self._roots[self._cur_tree].__next__()

        return self._cur_node

    def __eq__(self, other: Forest):
        if len(self._roots) != len(other._roots):
            return False

        for index in range(len(self._roots)):
            if not self._roots[index].__eq__(other._roots[index]):
                return False
        return True

    # Returns vertical distance - positive, if the SECOND node is closer to the roots then the first one,
    #         horizontal distance - positive, if the SECOND node is closer to older roots and nodes then the first one.
    def calc_distance(self, first: ForestNode, second: ForestNode):
        self._validate_nodes(first, second)

        first_root_path = self.get_path_to_root(first, is_root_needed=True, is_itself_needed=True)
        second_root_path = self.get_path_to_root(second, is_root_needed=True, is_itself_needed=True)
        vertical_distance = len(first_root_path) - len(second_root_path)

        lowest_row_level = min(len(first_root_path), len(second_root_path)) - 1
        first_lowest_successor = first_root_path[-lowest_row_level-1]
        second_lowest_successor = first_root_path[-lowest_row_level-1]
        is_first_lower = len(first_root_path) < len(second_root_path)
        if id(first_root_path[-1]) == id(second_root_path[-1]):
            if first.is_root() or second.is_root():
                lowest_row = self._roots
            else:
                lowest_row = first.parent.successors if is_first_lower else second.parent.successors

            min_lowest_row_index = min(self.node_parent_index(first_lowest_successor),
                                       self.node_parent_index(second_lowest_successor))
            max_lowest_row_index = max(self.node_parent_index(first_lowest_successor),
                                       self.node_parent_index(second_lowest_successor))
            is_first_lefter = min_lowest_row_index == self.node_parent_index(first_lowest_successor)

        else:
            lowest_row = self._roots
            min_lowest_row_index = min(self._roots.index(first_lowest_successor),
                                       self._roots.index(second_lowest_successor))
            max_lowest_row_index = max(self._roots.index(first_lowest_successor),
                                       self._roots.index(second_lowest_successor))
            is_first_lefter = min_lowest_row_index == self._roots.index(first_lowest_successor)

        # Calc average part
        average_distance = 0
        average_node_num = len(lowest_row[min_lowest_row_index + 1: max_lowest_row_index])
        if average_node_num > 0:
            for lowest_row_node in lowest_row[min_lowest_row_index+1: max_lowest_row_index]:
                subtree_width = lowest_row_node.calc_subtree_width()
                average_distance += subtree_width
            average_distance += average_node_num + 1

        # Calc side parts
        if average_node_num > 0:
            if is_first_lefter:
                left_extra_distance = self.calc_left_part_subtree_width(first, first_lowest_successor)
                right_extra_distance = self.calc_right_part_subtree_width(second, second_lowest_successor)
            else:
                right_extra_distance = self.calc_left_part_subtree_width(second, second_lowest_successor)
                left_extra_distance = self.calc_right_part_subtree_width(first, first_lowest_successor)

            horizontal_distance = left_extra_distance + average_distance + right_extra_distance

        else:
            subroot = first if is_first_lefter else second
            successor = second if is_first_lefter else first
            horizontal_distance = self.calc_left_part_subtree_width(successor, subroot)

        if is_first_lefter:
            horizontal_distance *= -1

        return vertical_distance, horizontal_distance

    @property
    def roots(self):
        return self._roots


    def calc_width(self):
        width = 0
        for root in self._roots:
            width += root.calc_subtree_width()
        return width

    def calc_left_part_subtree_width(self, section_node: Node, subroot: Node):
        width = 0
        cur_node = section_node
        while id(cur_node) != id(subroot):
            node_index = cur_node.index_by_parent()
            for sibling in cur_node.parent.successors[:node_index]:
                width += sibling.calc_subtree_width()
            width += len(cur_node.parent.successors[:node_index]) - 1
            cur_node = cur_node.parent
        return width

    def calc_right_part_subtree_width(self, section_node: Node, subroot: Node):
        width = 0
        cur_node = section_node
        while id(cur_node) != id(subroot):
            node_index = cur_node.index_by_parent()
            for sibling in cur_node.parent.successors[node_index:]:
                width += sibling.calc_subtree_width()
            width += len(cur_node.parent.successors[:node_index]) - 1
            cur_node = cur_node.parent
        return width

    # TODO: Transfer to Node (with find_farest_leaf)
    def find_root(self, node: Node) -> Node:
        self._validate_nodes(node)
        if node.is_root():
            return node

        root_candidate = node.parent
        while root_candidate.is_successor():
            root_candidate = root_candidate.parent
        return root_candidate

    def find_furthest_leaf(self, node: Node) -> Node:
        self._validate_nodes(node)
        if node.is_leaf():
            return node

        leaf_candidate = node.successors[-1]
        while leaf_candidate.is_parent():
            leaf_candidate = leaf_candidate.successors[-1]
        return leaf_candidate

    def find_furthest_leaf_with_distance(self, node: Node) -> tuple[Node, int]:
        self._validate_nodes(node)
        if node.is_leaf():
            return node, 0

        leaf_candidate = node.successors[-1]
        distance = len(node.successors) - 1
        while leaf_candidate.is_parent():
            distance += len(leaf_candidate.successors) - 1
            leaf_candidate = leaf_candidate.successors[-1]
        return leaf_candidate, distance

    def get_siblings_from(self, node: Node) -> list[Node]:
        self._validate_nodes(node)
        if node.is_root():
            return []

        parent = node.parent
        node_index = parent.successors.index(node)
        siblings = parent.successors[node_index:]
        return siblings

    def get_path_to_root(self, node: Node, is_root_needed=False, is_itself_needed=False) -> list[Node]:
        self._validate_nodes(node)
        path = []

        if node.is_root():
            if is_root_needed or is_itself_needed:
                path.append(node)
            return path

        if is_itself_needed:
            path.append(node)
        if node.parent.is_root():
            if is_root_needed:
                path.append(node.parent)
            return path

        cur_ancestor = node.parent
        while cur_ancestor.is_successor():
            path.append(cur_ancestor)
            cur_ancestor = cur_ancestor.parent
        if is_root_needed:
            path.append(cur_ancestor)
        return path

    def node_parent_index(self, node: Node):
        self._validate_nodes(node)

        if node.is_successor():
            index = node.index_by_parent()
        else:
            index = self._roots.index(node)
        return index


    # Private part
    # TODO: Combine with Node.build_tree
    @staticmethod
    def _build_tree(nodes_list: list, forest: Forest, parent=None):
        root = Forest.ForestNode(forest)
        root.content = nodes_list[0]
        nodes_list = nodes_list[1:]

        if parent is not None:
            parent.successors.append(root)
            root.parent = parent

        for subtree in nodes_list:
            if type(subtree) == list:
                Forest._build_tree(subtree, forest, root)
            else:
                successor = Forest.ForestNode(forest)
                successor.content = subtree
                root.successors.append(successor)
                successor.parent = root

        return root

    def _create_node(self, content=None) -> ForestNode:
        return Forest.ForestNode(self, content)

    def _delete_node(self, node: ForestNode):
        node.set_forest_ref(None)
        node.disconnect()

    def _remove_subtree_from_forest(self, subroot: ForestNode):
        for successor in subroot.successors:
            self._remove_subtree_from_forest(successor)
        subroot.set_forest_ref(None)


# TODO: Rework all funcs to they sustain validity of the forest
    def _make_root(self, node: ForestNode):
        node.disconnect()
        self._roots.append(node)

    def _validate_nodes(self, *argv):
        for arg in argv:
            if not isinstance(arg, Forest.ForestNode):
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
        # TODO: Copy successors or not
        pass

    def create_root(self, node_type=Forest.ForestNode):
        raise Tree.AlreadyExistingRoot

    def free_node(self, node: Forest.ForestNode) -> Tree:
        # TODO: To implement
        pass

    def free_subtree(self, subroot: Forest.ForestNode) -> Tree:
        # TODO: To implement
        pass

    def _make_root(self, node: Forest.ForestNode):
        raise Tree.AlreadyExistingRoot
