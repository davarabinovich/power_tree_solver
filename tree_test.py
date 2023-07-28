
import unittest
from tree import *


def build_tree(subtrees, parent=None):
    root = Node()
    root.content = subtrees[0]
    subtrees = subtrees[1:]

    if parent is not None:
        parent.successors.append(root)
        root.parent = parent

    for subtree in subtrees:
        if type(subtree) == list:
            build_tree(subtree, root)
        else:
            successor = Node()
            successor.content = subtree
            root.successors.append(successor)
            successor.parent = root

    return root


class NodeFullTreeMatcher:
    expected: Node

    def __init__(self, expected):
        self.expected = expected

    def __eq__(self, other: Node):
        if self.expected.content != other.content:
            return False
        if len(self.expected.successors) != len(other.successors):
            return False

        for index in range(len(self.expected.successors)):
            successor_matcher = NodeFullTreeMatcher(self.expected.successors[index])
            if not successor_matcher.__eq__(other.successors[index]):
                return False

        return True


class TestNodeDisconnect(unittest.TestCase):
    def test_disconnect_leaf_from_none(self):
        tested_node = build_tree([3])
        proper_node = build_tree([3])
        tested_node.disconnect()
        self.fully_assert(tested_node, tested_node, proper_node, proper_node)

    def test_disconnect_subtree_from_none(self):
        tested_node = build_tree([3, 4, [9, 7, 5]])
        proper_node = build_tree([3, 4, [9, 7, 5]])
        tested_node.disconnect()
        self.fully_assert(tested_node, tested_node, proper_node, proper_node)

    def test_disconnect_leaf_from_root(self):
        tested_root = build_tree([1, [2, 9, [8, 5, 7, 2], 8], 5, [3, 4, [5, 6, 7], [2, 5, 9]], 7])
        tested_node = tested_root.successors[1]
        proper_root = build_tree([1, [2, 9, [8, 5, 7, 2], 8], [3, 4, [5, 6, 7], [2, 5, 9]], 7])
        proper_node = build_tree([5])

        tested_node.disconnect()
        self.fully_assert(tested_node, tested_root, proper_node, proper_root)

    def test_disconnect_subtree_from_root(self):
        tested_root = build_tree([1, [2, 9, [8, 5, 7, 2], 8], 5, [3, 4, [5, 6, 7], [2, 5, 9]], 7])
        tested_node = tested_root.successors[0]
        proper_root = build_tree([1, 5, [3, 4, [5, 6, 7], [2, 5, 9]], 7])
        proper_node = build_tree([2, 9, [8, 5, 7, 2], 8])

        tested_node.disconnect()
        self.fully_assert(tested_node, tested_root, proper_node, proper_root)

    def test_disconnect_leaf_from_inner_node(self):
        tested_root = build_tree([1, [2, 9, [8, 5, 7, 2], 8], 5, [3, 4, [5, 6, 7, 1, 8, 0, 4], [2, 5, 9]], 7])
        tested_node = tested_root.successors[2].successors[1].successors[5]
        proper_root = build_tree([1, [2, 9, [8, 5, 7, 2], 8], 5, [3, 4, [5, 6, 7, 1, 8, 0], [2, 5, 9]], 7])
        proper_node = build_tree([4])

        tested_node.disconnect()
        self.fully_assert(tested_node, tested_root, proper_node, proper_root)

    def test_disconnect_subtree_from_inner_node(self):
        tested_root = build_tree([1, [2, 9, [8, 5, 7, 2], 8], 5, [3, 4, [5, 6, 7], [2, 5, 9]], 7])
        tested_node = tested_root.successors[2].successors[2]
        proper_root = build_tree([1, [2, 9, [8, 5, 7, 2], 8], 5, [3, 4, [5, 6, 7]], 7])
        proper_node = build_tree([2, 5, 9])

        tested_node.disconnect()
        self.fully_assert(tested_node, tested_root, proper_node, proper_root)

    def fully_assert(self, tested_node: Node, tested_root: Node, proper_node: Node, proper_root: Node):
        self.assertEqual(None, tested_node.parent)
        self.assertEqual(NodeFullTreeMatcher(proper_node), tested_node)
        self.assertEqual(NodeFullTreeMatcher(proper_root), tested_root)

    # def test_connect_to(self):
    #     pass
        # TODO: Test connect to root, node above, node below, leaf,
        #       inner and terminal successors, None, root, inner node and leaf in another Tree

# TODO: Test deletion
class TestForest(unittest.TestCase):
    pass

class TestTree(unittest.TestCase):
    pass
    # TODO: Test tree-specific content and some forest functions on tree

if __name__ == '__main__':
    unittest.main()
