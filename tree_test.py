
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

    def test_disconnect_last_leaf(self):
        tested_root = build_tree([1, [2, 9], 5, 7])
        tested_node = tested_root.successors[0].successors[0]
        proper_root = build_tree([1, 2, 5, 7])
        proper_node = build_tree([9])

        tested_node.disconnect()
        self.fully_assert(tested_node, tested_root, proper_node, proper_root)

    def test_disconnect_last_subtree(self):
        tested_root = build_tree([1, [2, 9, [8, 5, 7, 2], 8]])
        tested_node = tested_root.successors[0]
        proper_root = build_tree([1])
        proper_node = build_tree([2, 9, [8, 5, 7, 2], 8])

        tested_node.disconnect()
        self.fully_assert(tested_node, tested_root, proper_node, proper_root)


    def fully_assert(self, tested_node: Node, tested_root: Node, proper_node: Node, proper_root: Node):
        self.assertEqual(None, tested_node.parent)
        self.assertEqual(NodeFullTreeMatcher(proper_node), tested_node)
        self.assertEqual(NodeFullTreeMatcher(proper_root), tested_root)


class TestNodeConnectTo(unittest.TestCase):
    def test_connect_leaf_to_root(self):
        tested_root = build_tree([1, [2, 9, [8, 5, 7, 2], 8], 5, [3, 4, [5, 6, 7], [2, 5, 9]], 7])
        tested_node = tested_root.successors[2].successors[0]
        proper_root = build_tree([1, [2, 9, [8, 5, 7, 2], 8], 5, [3, [5, 6, 7], [2, 5, 9]], 7, 4])
        tested_node.connect_to(tested_root)
        self.assertEqual(NodeFullTreeMatcher(proper_root), tested_root)

    def test_connect_subtree_to_root(self):
        tested_root = build_tree([1, [2, 9, [8, 5, 7, 2], 8], 5, [3, 4, [5, 6, 7], [2, 5, 9]], 7])
        tested_node = tested_root.successors[0].successors[1]
        proper_root = build_tree([1, [2, 9, 8], 5, [3, 4, [5, 6, 7], [2, 5, 9]], 7, [8, 5, 7, 2]])
        tested_node.connect_to(tested_root)
        self.assertEqual(NodeFullTreeMatcher(proper_root), tested_root)

    def test_connect_leaf_to_node_above(self):
        tested_root = build_tree([1, [2, 9, [8, 5, 7, 2], 8], 5, [3, 4, [5, 6, 7], [2, 5, 9]], 7])
        tested_node = tested_root.successors[0].successors[1].successors[1]
        tested_parent = tested_root.successors[2]
        proper_root = build_tree([1, [2, 9, [8, 5, 2], 8], 5, [3, 4, [5, 6, 7], [2, 5, 9], 7], 7])

        tested_node.connect_to(tested_parent)
        self.assertEqual(NodeFullTreeMatcher(proper_root), tested_root)

    def test_connect_subtree_to_node_above(self):
        tested_root = build_tree([1, [2, 9, [8, 5, 7, 2], 8], 5, [3, 4, [5, [6, 9, 0], 7], [2, 5, 9]], 7])
        tested_node = tested_root.successors[2].successors[1].successors[0]
        tested_parent = tested_root.successors[2]
        proper_root = build_tree([1, [2, 9, [8, 5, 7, 2], 8], 5, [3, 4, [5, 7], [2, 5, 9], [6, 9, 0]], 7])

        tested_node.connect_to(tested_parent)
        self.assertEqual(NodeFullTreeMatcher(proper_root), tested_root)

    def test_connect_leaf_to_node_below(self):
        tested_root = build_tree([1, [2, 9, [8, 5, 7, 2], 8], 5, [3, 4, [5, 6, 7], [2, 5, 9]], 7])
        tested_node = tested_root.successors[1]
        tested_parent = tested_root.successors[2].successors[1]
        proper_root = build_tree([1, [2, 9, [8, 5, 7, 2], 8], [3, 4, [5, 6, 7, 5], [2, 5, 9]], 7])

        tested_node.connect_to(tested_parent)
        self.assertEqual(NodeFullTreeMatcher(proper_root), tested_root)

    def test_connect_subtree_to_node_below(self):
        tested_root = build_tree([1, [2, 9, [8, 5, 7, 2], 8], 5, [3, 4, [5, [6, 9, 0], 7], [2, 5, 9]], 7])
        tested_node = tested_root.successors[0].successors[1]
        tested_parent = tested_root.successors[2].successors[1].successors[0].successors[0]
        proper_root = build_tree([1, [2, 9, 8], 5, [3, 4, [5, [6, [9, [8, 5, 7, 2]], 0], 7], [2, 5, 9]], 7])

        tested_node.connect_to(tested_parent)
        self.assertEqual(NodeFullTreeMatcher(proper_root), tested_root)

    def test_connect_leaf_to_leaf(self):
        tested_root = build_tree([1, [2, 9, [8, 5, 7, 2], 8], 5, [3, 4, [5, 6, 7], [2, 5, 9]], 7])
        tested_node = tested_root.successors[1]
        tested_parent = tested_root.successors[2].successors[2].successors[1]
        proper_root = build_tree([1, [2, 9, [8, 5, 7, 2], 8], [3, 4, [5, 6, 7], [2, 5, [9, 5]]], 7])

        tested_node.connect_to(tested_parent)
        self.assertEqual(NodeFullTreeMatcher(proper_root), tested_root)

    def test_connect_subtree_to_leaf(self):
        tested_root = build_tree([1, [2, 9, [8, 5, 7, 2], 8], 5, [3, 4, [5, [6, 9, 0], 7], [2, 5, 9]], 7])
        tested_node = tested_root.successors[2].successors[2]
        tested_parent = tested_root.successors[3]
        proper_root = build_tree([1, [2, 9, [8, 5, 7, 2], 8], 5, [3, 4, [5, [6, 9, 0], 7]], [7, [2, 5, 9]]])

        tested_node.connect_to(tested_parent)
        self.assertEqual(NodeFullTreeMatcher(proper_root), tested_root)

    def test_connect_leaf_to_alone_node(self):
        tested_root = build_tree([1, [2, 9, [8, 5, 7, 2], 8], 5, [3, 4, [5, [6, 9, 0], 7], [2, 5, 9]], 7])
        tested_node = tested_root.successors[0].successors[1].successors[1]
        tested_parent = build_tree([0])
        proper_root = build_tree([1, [2, 9, [8, 5, 2], 8], 5, [3, 4, [5, [6, 9, 0], 7], [2, 5, 9]], 7])
        proper_alien_root = build_tree([0, 7])

        tested_node.connect_to(tested_parent)
        self.assertEqual(NodeFullTreeMatcher(proper_root), tested_root)
        self.assertEqual(NodeFullTreeMatcher(proper_alien_root), tested_parent)

    def test_connect_subtree_to_alone_node(self):
        tested_root = build_tree([1, [2, 9, [8, 5, 7, 2], 8], 5, [3, 4, [5, [6, 9, 0], 7], [2, 5, 9]], 7])
        tested_node = tested_root.successors[2].successors[2]
        tested_parent = build_tree([0])
        proper_root = build_tree([1, [2, 9, [8, 5, 7, 2], 8], 5, [3, 4, [5, [6, 9, 0], 7]], 7])
        proper_alien_root = build_tree([0, [2, 5, 9]])

        tested_node.connect_to(tested_parent)
        self.assertEqual(NodeFullTreeMatcher(proper_root), tested_root)
        self.assertEqual(NodeFullTreeMatcher(proper_alien_root), tested_parent)

    def test_connect_root_to_alone_node(self):
        tested_root = build_tree([1, [2, 9, [8, 5, 7, 2], 8], 5, [3, 4, [5, [6, 9, 0], 7], [2, 5, 9]], 7])
        tested_parent = build_tree([0])
        proper_root = build_tree([1, [2, 9, [8, 5, 7, 2], 8], 5, [3, 4, [5, [6, 9, 0], 7], [2, 5, 9]], 7])
        proper_alien_root = build_tree([0, [1, [2, 9, [8, 5, 7, 2], 8], 5, [3, 4, [5, [6, 9, 0], 7], [2, 5, 9]], 7]])

        tested_root.connect_to(tested_parent)
        self.assertEqual(NodeFullTreeMatcher(proper_root), tested_root)
        self.assertEqual(NodeFullTreeMatcher(proper_alien_root), tested_parent)

    def test_connect_subtree_to_alien_root(self):
        tested_root = build_tree([1, [2, 9, [8, 5, 7, 2], 8], 5, [3, 4, [5, [6, 9, 0], 7], [2, 5, 9]], 7])
        tested_node = tested_root.successors[2].successors[2]
        tested_alien_root = build_tree([0, [9, 0, 4], [2, [2, 5, 6]], 7])

        proper_root = build_tree([1, [2, 9, [8, 5, 7, 2], 8], 5, [3, 4, [5, [6, 9, 0], 7]], 7])
        proper_alien_root = build_tree([0, [9, 0, 4], [2, [2, 5, 6]], 7, [2, 5, 9]])

        tested_node.connect_to(tested_alien_root)
        self.assertEqual(NodeFullTreeMatcher(proper_root), tested_root)
        self.assertEqual(NodeFullTreeMatcher(proper_alien_root), tested_alien_root)

    def test_connect_subtree_to_alien_inner_node(self):
        tested_root = build_tree([1, [2, 9, [8, 5, 7, 2], 8], 5, [3, 4, [5, [6, 9, 0], 7], [2, 5, 9]], 7])
        tested_node = tested_root.successors[2].successors[2]
        tested_alien_root = build_tree([0, [9, 0, 4], [2, [2, 5, 6]], 7])
        tested_parent = tested_alien_root.successors[0].successors[0]

        proper_root = build_tree([1, [2, 9, [8, 5, 7, 2], 8], 5, [3, 4, [5, [6, 9, 0], 7]], 7])
        proper_alien_root = build_tree([0, [9, [0, [2, 5, 9]], 4], [2, [2, 5, 6]], 7])

        tested_node.connect_to(tested_parent)
        self.assertEqual(NodeFullTreeMatcher(proper_root), tested_root)
        self.assertEqual(NodeFullTreeMatcher(proper_alien_root), tested_alien_root)

    def test_connect_subtree_to_alien_leaf(self):
        tested_root = build_tree([1, [2, 9, [8, 5, 7, 2], 8], 5, [3, 4, [5, [6, 9, 0], 7], [2, 5, 9]], 7])
        tested_node = tested_root.successors[2].successors[2]
        tested_alien_root = build_tree([0, [9, 0, 4], [2, [2, 5, 6]], 7])
        tested_parent = tested_alien_root.successors[1].successors[0].successors[1]

        proper_root = build_tree([1, [2, 9, [8, 5, 7, 2], 8], 5, [3, 4, [5, [6, 9, 0], 7]], 7])
        proper_alien_root = build_tree([0, [9, 0, 4], [2, [2, 5, [6, [2, 5, 9]]]], 7])

        tested_node.connect_to(tested_parent)
        self.assertEqual(NodeFullTreeMatcher(proper_root), tested_root)
        self.assertEqual(NodeFullTreeMatcher(proper_alien_root), tested_alien_root)

        # TODO: Cycling connection, connection removing last leaf

# TODO: Test deletion and other public methods
class TestForest(unittest.TestCase):
    pass

class TestTree(unittest.TestCase):
    pass
    # TODO: Test tree-specific content and some forest functions on tree

if __name__ == '__main__':
    unittest.main()
