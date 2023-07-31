
import unittest
from tree import *


# class NodeFullForestMatcher:
#     expected: Forest
#
#     def __init__(self, expected):
#         self.expected = expected
#
#     def __eq__(self, other: Forest):
#         if not is_forest_valid(self.expected):
#             return False
#         if not is_forest_valid(other):
#             return False
#
#         for len(self.expected._roots) != len(other.roots):
#             return False
#
#         if self.expected.content != other.content:
#             return False
#         if len(self.expected.successors) != len(other.successors):
#             return False
#
#         for index in range(len(self.expected.successors)):
#             successor_matcher = self.expected.successors[index])
#             if not successor_matcher.__eq__(other.successors[index]):
#                 return False
#
#         return True


def is_subtree_valid(root: Node):
    for successor in root.successors:
        if successor.parent != root:
            return False
        is_subtree_valid(successor)
    return True

def is_forest_valid(forest: Forest):
    for root in forest.roots():
        is_forest_tree_valid(root, forest)

def is_forest_tree_valid(root: Forest._ForestNode, forest:Forest):
    if root.get_forest_ref() != forest:
        return False

    for successor in root.successors:
        if successor.parent != root:
            return False
        is_subtree_valid(successor)
    return True


class TestNodeDisconnect(unittest.TestCase):
    def test_disconnect_leaf_from_none(self):
        tested_node = Node.build_tree([3])
        proper_node = Node.build_tree([3])
        tested_node.disconnect()
        self.fully_assert(tested_node, tested_node, proper_node, proper_node)

    def test_disconnect_subtree_from_none(self):
        tested_node = Node.build_tree([3, 4, [9, 7, 5]])
        proper_node = Node.build_tree([3, 4, [9, 7, 5]])
        tested_node.disconnect()
        self.fully_assert(tested_node, tested_node, proper_node, proper_node)

    def test_disconnect_leaf_from_root(self):
        tested_root = Node.build_tree([1, [2, 9, [8, 5, 7, 2], 8], 5, [3, 4, [5, 6, 7], [2, 5, 9]], 7])
        tested_node = tested_root.successors[1]
        proper_root = Node.build_tree([1, [2, 9, [8, 5, 7, 2], 8], [3, 4, [5, 6, 7], [2, 5, 9]], 7])
        proper_node = Node.build_tree([5])

        tested_node.disconnect()
        self.fully_assert(tested_node, tested_root, proper_node, proper_root)

    def test_disconnect_subtree_from_root(self):
        tested_root = Node.build_tree([1, [2, 9, [8, 5, 7, 2], 8], 5, [3, 4, [5, 6, 7], [2, 5, 9]], 7])
        tested_node = tested_root.successors[0]
        proper_root = Node.build_tree([1, 5, [3, 4, [5, 6, 7], [2, 5, 9]], 7])
        proper_node = Node.build_tree([2, 9, [8, 5, 7, 2], 8])

        tested_node.disconnect()
        self.fully_assert(tested_node, tested_root, proper_node, proper_root)

    def test_disconnect_leaf_from_inner_node(self):
        tested_root = Node.build_tree([1, [2, 9, [8, 5, 7, 2], 8], 5, [3, 4, [5, 6, 7, 1, 8, 0, 4], [2, 5, 9]], 7])
        tested_node = tested_root.successors[2].successors[1].successors[5]
        proper_root = Node.build_tree([1, [2, 9, [8, 5, 7, 2], 8], 5, [3, 4, [5, 6, 7, 1, 8, 0], [2, 5, 9]], 7])
        proper_node = Node.build_tree([4])

        tested_node.disconnect()
        self.fully_assert(tested_node, tested_root, proper_node, proper_root)

    def test_disconnect_subtree_from_inner_node(self):
        tested_root = Node.build_tree([1, [2, 9, [8, 5, 7, 2], 8], 5, [3, 4, [5, 6, 7], [2, 5, 9]], 7])
        tested_node = tested_root.successors[2].successors[2]
        proper_root = Node.build_tree([1, [2, 9, [8, 5, 7, 2], 8], 5, [3, 4, [5, 6, 7]], 7])
        proper_node = Node.build_tree([2, 5, 9])

        tested_node.disconnect()
        self.fully_assert(tested_node, tested_root, proper_node, proper_root)

    def test_disconnect_last_leaf(self):
        tested_root = Node.build_tree([1, [2, 9], 5, 7])
        tested_node = tested_root.successors[0].successors[0]
        proper_root = Node.build_tree([1, 2, 5, 7])
        proper_node = Node.build_tree([9])

        tested_node.disconnect()
        self.fully_assert(tested_node, tested_root, proper_node, proper_root)

    def test_disconnect_last_subtree(self):
        tested_root = Node.build_tree([1, [2, 9, [8, 5, 7, 2], 8]])
        tested_node = tested_root.successors[0]
        proper_root = Node.build_tree([1])
        proper_node = Node.build_tree([2, 9, [8, 5, 7, 2], 8])

        tested_node.disconnect()
        self.fully_assert(tested_node, tested_root, proper_node, proper_root)


    def fully_assert(self, tested_node: Node, tested_root: Node, proper_node: Node, proper_root: Node):
        self.assertEqual(None, tested_node.parent)
        self.assertTrue(is_subtree_valid(tested_root))
        self.assertEqual(proper_node, tested_node)
        self.assertEqual(proper_root, tested_root)


class TestNodeConnectTo(unittest.TestCase):
    def test_connect_leaf_to_root(self):
        tested_root = Node.build_tree([1, [2, 9, [8, 5, 7, 2], 8], 5, [3, 4, [5, 6, 7], [2, 5, 9]], 7])
        tested_node = tested_root.successors[2].successors[0]
        proper_root = Node.build_tree([1, [2, 9, [8, 5, 7, 2], 8], 5, [3, [5, 6, 7], [2, 5, 9]], 7, 4])

        tested_node.connect_to(tested_root)
        self.assertTrue(is_subtree_valid(tested_root))
        self.assertEqual(proper_root, tested_root)

    def test_connect_subtree_to_root(self):
        tested_root = Node.build_tree([1, [2, 9, [8, 5, 7, 2], 8], 5, [3, 4, [5, 6, 7], [2, 5, 9]], 7])
        tested_node = tested_root.successors[0].successors[1]
        proper_root = Node.build_tree([1, [2, 9, 8], 5, [3, 4, [5, 6, 7], [2, 5, 9]], 7, [8, 5, 7, 2]])

        tested_node.connect_to(tested_root)
        self.assertTrue(is_subtree_valid(tested_root))
        self.assertEqual(proper_root, tested_root)

    def test_connect_leaf_to_node_above(self):
        tested_root = Node.build_tree([1, [2, 9, [8, 5, 7, 2], 8], 5, [3, 4, [5, 6, 7], [2, 5, 9]], 7])
        tested_node = tested_root.successors[0].successors[1].successors[1]
        tested_parent = tested_root.successors[2]
        proper_root = Node.build_tree([1, [2, 9, [8, 5, 2], 8], 5, [3, 4, [5, 6, 7], [2, 5, 9], 7], 7])

        tested_node.connect_to(tested_parent)
        self.assertTrue(is_subtree_valid(tested_root))
        self.assertEqual(proper_root, tested_root)

    def test_connect_subtree_to_node_above(self):
        tested_root = Node.build_tree([1, [2, 9, [8, 5, 7, 2], 8], 5, [3, 4, [5, [6, 9, 0], 7], [2, 5, 9]], 7])
        tested_node = tested_root.successors[2].successors[1].successors[0]
        tested_parent = tested_root.successors[2]
        proper_root = Node.build_tree([1, [2, 9, [8, 5, 7, 2], 8], 5, [3, 4, [5, 7], [2, 5, 9], [6, 9, 0]], 7])

        tested_node.connect_to(tested_parent)
        self.assertTrue(is_subtree_valid(tested_root))
        self.assertEqual(proper_root, tested_root)

    def test_connect_leaf_to_node_below(self):
        tested_root = Node.build_tree([1, [2, 9, [8, 5, 7, 2], 8], 5, [3, 4, [5, 6, 7], [2, 5, 9]], 7])
        tested_node = tested_root.successors[1]
        tested_parent = tested_root.successors[2].successors[1]
        proper_root = Node.build_tree([1, [2, 9, [8, 5, 7, 2], 8], [3, 4, [5, 6, 7, 5], [2, 5, 9]], 7])

        tested_node.connect_to(tested_parent)
        self.assertTrue(is_subtree_valid(tested_root))
        self.assertEqual(proper_root, tested_root)

    def test_connect_subtree_to_node_below(self):
        tested_root = Node.build_tree([1, [2, 9, [8, 5, 7, 2], 8], 5, [3, 4, [5, [6, 9, 0], 7], [2, 5, 9]], 7])
        tested_node = tested_root.successors[0].successors[1]
        tested_parent = tested_root.successors[2].successors[1].successors[0].successors[0]
        proper_root = Node.build_tree([1, [2, 9, 8], 5, [3, 4, [5, [6, [9, [8, 5, 7, 2]], 0], 7], [2, 5, 9]], 7])

        tested_node.connect_to(tested_parent)
        self.assertTrue(is_subtree_valid(tested_root))
        self.assertEqual(proper_root, tested_root)

    def test_connect_leaf_to_leaf(self):
        tested_root = Node.build_tree([1, [2, 9, [8, 5, 7, 2], 8], 5, [3, 4, [5, 6, 7], [2, 5, 9]], 7])
        tested_node = tested_root.successors[1]
        tested_parent = tested_root.successors[2].successors[2].successors[1]
        proper_root = Node.build_tree([1, [2, 9, [8, 5, 7, 2], 8], [3, 4, [5, 6, 7], [2, 5, [9, 5]]], 7])

        tested_node.connect_to(tested_parent)
        self.assertTrue(is_subtree_valid(tested_root))
        self.assertEqual(proper_root, tested_root)

    def test_connect_subtree_to_leaf(self):
        tested_root = Node.build_tree([1, [2, 9, [8, 5, 7, 2], 8], 5, [3, 4, [5, [6, 9, 0], 7], [2, 5, 9]], 7])
        tested_node = tested_root.successors[2].successors[2]
        tested_parent = tested_root.successors[3]
        proper_root = Node.build_tree([1, [2, 9, [8, 5, 7, 2], 8], 5, [3, 4, [5, [6, 9, 0], 7]], [7, [2, 5, 9]]])

        tested_node.connect_to(tested_parent)
        self.assertTrue(is_subtree_valid(tested_root))
        self.assertEqual(proper_root, tested_root)

    def test_connect_leaf_to_alone_node(self):
        tested_root = Node.build_tree([1, [2, 9, [8, 5, 7, 2], 8], 5, [3, 4, [5, [6, 9, 0], 7], [2, 5, 9]], 7])
        tested_node = tested_root.successors[0].successors[1].successors[1]
        tested_parent = Node.build_tree([0])
        proper_root = Node.build_tree([1, [2, 9, [8, 5, 2], 8], 5, [3, 4, [5, [6, 9, 0], 7], [2, 5, 9]], 7])
        proper_alien_root = Node.build_tree([0, 7])

        tested_node.connect_to(tested_parent)
        self.assertTrue(is_subtree_valid(tested_root))
        self.assertTrue(is_subtree_valid(tested_parent))
        self.assertEqual(proper_root, tested_root)
        self.assertEqual(proper_alien_root, tested_parent)

    def test_connect_subtree_to_alone_node(self):
        tested_root = Node.build_tree([1, [2, 9, [8, 5, 7, 2], 8], 5, [3, 4, [5, [6, 9, 0], 7], [2, 5, 9]], 7])
        tested_node = tested_root.successors[2].successors[2]
        tested_parent = Node.build_tree([0])
        proper_root = Node.build_tree([1, [2, 9, [8, 5, 7, 2], 8], 5, [3, 4, [5, [6, 9, 0], 7]], 7])
        proper_alien_root = Node.build_tree([0, [2, 5, 9]])

        tested_node.connect_to(tested_parent)
        self.assertTrue(is_subtree_valid(tested_root))
        self.assertTrue(is_subtree_valid(tested_parent))
        self.assertEqual(proper_root, tested_root)
        self.assertEqual(proper_alien_root, tested_parent)

    def test_connect_root_to_alone_node(self):
        tested_root = Node.build_tree([1, [2, 9, [8, 5, 7, 2], 8], 5, [3, 4, [5, [6, 9, 0], 7], [2, 5, 9]], 7])
        tested_parent = Node.build_tree([0])
        proper_root = Node.build_tree([1, [2, 9, [8, 5, 7, 2], 8], 5, [3, 4, [5, [6, 9, 0], 7], [2, 5, 9]], 7])
        proper_alien_root = Node.build_tree([0, [1, [2, 9, [8, 5, 7, 2], 8], 5, [3, 4, [5, [6, 9, 0], 7], [2, 5, 9]], 7]])

        tested_root.connect_to(tested_parent)
        self.assertTrue(is_subtree_valid(tested_root))
        self.assertTrue(is_subtree_valid(tested_parent))
        self.assertEqual(proper_root, tested_root)
        self.assertEqual(proper_alien_root, tested_parent)

    def test_connect_subtree_to_alien_root(self):
        tested_root = Node.build_tree([1, [2, 9, [8, 5, 7, 2], 8], 5, [3, 4, [5, [6, 9, 0], 7], [2, 5, 9]], 7])
        tested_node = tested_root.successors[2].successors[2]
        tested_alien_root = Node.build_tree([0, [9, 0, 4], [2, [2, 5, 6]], 7])

        proper_root = Node.build_tree([1, [2, 9, [8, 5, 7, 2], 8], 5, [3, 4, [5, [6, 9, 0], 7]], 7])
        proper_alien_root = Node.build_tree([0, [9, 0, 4], [2, [2, 5, 6]], 7, [2, 5, 9]])

        tested_node.connect_to(tested_alien_root)
        self.assertTrue(is_subtree_valid(tested_root))
        self.assertTrue(is_subtree_valid(tested_alien_root))
        self.assertEqual(proper_root, tested_root)
        self.assertEqual(proper_alien_root, tested_alien_root)

    def test_connect_subtree_to_alien_inner_node(self):
        tested_root = Node.build_tree([1, [2, 9, [8, 5, 7, 2], 8], 5, [3, 4, [5, [6, 9, 0], 7], [2, 5, 9]], 7])
        tested_node = tested_root.successors[2].successors[2]
        tested_alien_root = Node.build_tree([0, [9, 0, 4], [2, [2, 5, 6]], 7])
        tested_parent = tested_alien_root.successors[0].successors[0]

        proper_root = Node.build_tree([1, [2, 9, [8, 5, 7, 2], 8], 5, [3, 4, [5, [6, 9, 0], 7]], 7])
        proper_alien_root = Node.build_tree([0, [9, [0, [2, 5, 9]], 4], [2, [2, 5, 6]], 7])

        tested_node.connect_to(tested_parent)
        self.assertTrue(is_subtree_valid(tested_root))
        self.assertTrue(is_subtree_valid(tested_alien_root))
        self.assertEqual(proper_root, tested_root)
        self.assertEqual(proper_alien_root, tested_alien_root)

    def test_connect_subtree_to_alien_leaf(self):
        tested_root = Node.build_tree([1, [2, 9, [8, 5, 7, 2], 8], 5, [3, 4, [5, [6, 9, 0], 7], [2, 5, 9]], 7])
        tested_node = tested_root.successors[2].successors[2]
        tested_alien_root = Node.build_tree([0, [9, 0, 4], [2, [2, 5, 6]], 7])
        tested_parent = tested_alien_root.successors[1].successors[0].successors[1]

        proper_root = Node.build_tree([1, [2, 9, [8, 5, 7, 2], 8], 5, [3, 4, [5, [6, 9, 0], 7]], 7])
        proper_alien_root = Node.build_tree([0, [9, 0, 4], [2, [2, 5, [6, [2, 5, 9]]]], 7])

        tested_node.connect_to(tested_parent)
        self.assertTrue(is_subtree_valid(tested_root))
        self.assertTrue(is_subtree_valid(tested_alien_root))
        self.assertEqual(proper_root, tested_root)
        self.assertEqual(proper_alien_root, tested_alien_root)

    def test_reconnect_last_leaf(self):
        tested_root = Node.build_tree([1, [2, 9], 5, [3, 4, [5, [6, 9, 0], 7], [2, 5, 9]], 7])
        tested_node = tested_root.successors[0].successors[0]
        tested_parent = tested_root.successors[1]
        proper_root = Node.build_tree([1, 2, [5, 9], [3, 4, [5, [6, 9, 0], 7], [2, 5, 9]], 7])

        tested_node.connect_to(tested_parent)
        self.assertTrue(is_subtree_valid(tested_root))
        self.assertEqual(proper_root, tested_root)

    def test_reconnect_last_subtree(self):
        tested_root = Node.build_tree([1, [2, 9], 5, [3, 4, [5, [6, 9, 0]], [2, 5, 9]], 7])
        tested_node = tested_root.successors[2].successors[1].successors[0]
        tested_parent = tested_root.successors[0]
        proper_root = Node.build_tree([1, [2, 9, [6, 9, 0]], 5, [3, 4, 5, [2, 5, 9]], 7])

        tested_node.connect_to(tested_parent)
        self.assertTrue(is_subtree_valid(tested_root))
        self.assertEqual(proper_root, tested_root)

    def test_closing_connection_subtree_to_leaf(self):
        tested_root = Node.build_tree([1, [2, 9], 5, [3, 4, [5, [6, 9, 0]], [2, 5, 9]], 7])
        tested_node = tested_root.successors[2]
        tested_parent = tested_root.successors[2].successors[1].successors[0].successors[1]
        with self.assertRaises(Node.ClosingTransition):
            tested_node.connect_to(tested_parent)

    def test_closing_connection_subtree_to_subtree(self):
        tested_root = Node.build_tree([1, [2, 9], 5, [3, 4, [5, [6, 9, 0]], [2, 5, 9]], 7])
        tested_node = tested_root.successors[2]
        tested_parent = tested_root.successors[2].successors[1].successors[0]
        with self.assertRaises(Node.ClosingTransition):
            tested_node.connect_to(tested_parent)

    def test_closing_connection_root_to_leaf(self):
        tested_root = Node.build_tree([1, [2, 9], 5, [3, 4, [5, [6, 9, 0]], [2, 5, 9]], 7])
        tested_parent = tested_root.successors[2].successors[1].successors[0].successors[1]
        with self.assertRaises(Node.ClosingTransition):
            tested_root.connect_to(tested_parent)

    def test_closing_connection_root_to_subtree(self):
        tested_root = Node.build_tree([1, [2, 9], 5, [3, 4, [5, [6, 9, 0]], [2, 5, 9]], 7])
        tested_parent = tested_root.successors[2].successors[1].successors[0]
        with self.assertRaises(Node.ClosingTransition):
            tested_root.connect_to(tested_parent)


class TestNodeReplaceWith(unittest.TestCase):
    def test_replace_root_with_inner_node(self):
        tested_root = Node.build_tree([1, [2, 9, [8, 5, 7, 2], 8], 5, [3, 4, [5, 6, 7], [2, 5, 9]], 7])
        tested_node = tested_root.successors[0].successors[1]
        proper_root = Node.build_tree([1, [2, 9, 8], 5, [3, 4, [5, 6, 7], [2, 5, 9]], 7])
        proper_node = Node.build_tree([8, 5, 7, 2])

        tested_root.replace_with(tested_node)
        self.assertEqual(None, tested_root.parent)
        self.fully_assert(tested_node, tested_root, proper_node, proper_root)

    def test_replace_root_with_leaf(self):
        tested_root = Node.build_tree([1, [2, 9, [8, 5, 7, 2], 8], 5, [3, 4, [5, 6, 7], [2, 5, 9]], 7])
        tested_node = tested_root.successors[1]
        proper_root = Node.build_tree([1, [2, 9, [8, 5, 7, 2], 8], [3, 4, [5, 6, 7], [2, 5, 9]], 7])
        proper_node = Node.build_tree([5])

        tested_root.replace_with(tested_node)
        self.assertEqual(None, tested_root.parent)
        self.fully_assert(tested_node, tested_root, proper_node, proper_root)

    def test_replace_subtree_with_node_above(self):
        tested_root = Node.build_tree([1, [2, 9, [8, 5, 7, 2], 8], 5, [3, 4, [5, 6, 7], [2, 5, 9]], 7])
        tested_node = tested_root.successors[0].successors[1]
        replacement = tested_root.successors[2]
        proper_root = Node.build_tree([1, [2, 9, [3, 4, [5, 6, 7], [2, 5, 9]], 8], 5, 7])
        proper_node = Node.build_tree([8, 5, 7, 2])

        tested_node.replace_with(replacement)
        self.fully_assert(tested_node, tested_root, proper_node, proper_root)

    def test_replace_subtree_with_node_below(self):
        tested_root = Node.build_tree([1, [2, 9, [8, 5, 7, 2], 8], 5, [3, 4, [5, 6, 7], [2, 5, 9]], 7])
        tested_node = tested_root.successors[0]
        replacement = tested_root.successors[2].successors[1]
        proper_root = Node.build_tree([1, [5, 6, 7], 5, [3, 4, [2, 5, 9]], 7])
        proper_node = Node.build_tree([2, 9, [8, 5, 7, 2], 8])

        tested_node.replace_with(replacement)
        self.fully_assert(tested_node, tested_root, proper_node, proper_root)

    def test_replace_subtree_with_leaf(self):
        tested_root = Node.build_tree([1, [2, 9, [8, 5, 7, 2], 8], 5, [3, 4, [5, 6, 7], [2, 5, 9]], 7])
        tested_node = tested_root.successors[0].successors[1].successors[1]
        replacement = tested_root.successors[2]
        proper_root = Node.build_tree([1, [2, 9, [8, 5, [3, 4, [5, 6, 7], [2, 5, 9]], 2], 8], 5, 7])
        proper_node = Node.build_tree([7])

        tested_node.replace_with(replacement)
        self.fully_assert(tested_node, tested_root, proper_node, proper_root)

    def test_replace_leaf_with_subtree(self):
        tested_root = Node.build_tree([1, [2, 9, [8, 5, 7, 2], 8], 5, [3, 4, [5, 6, 7], [2, 5, 9]], 7])
        tested_node = tested_root.successors[2].successors[0]
        replacement = tested_root.successors[2].successors[1]
        proper_root = Node.build_tree([1, [2, 9, [8, 5, 7, 2], 8], 5, [3, [5, 6, 7], [2, 5, 9]], 7])
        proper_node = Node.build_tree([4])

        tested_node.replace_with(replacement)
        self.fully_assert(tested_node, tested_root, proper_node, proper_root)

    def test_replace_leaf_with_leaf(self):
        tested_root = Node.build_tree([1, [2, 9, [8, 5, 7, 2], 8], 5, [3, 4, [5, 6, 7], [2, 5, 9]], 7])
        tested_node = tested_root.successors[0].successors[1].successors[1]
        replacement = tested_root.successors[1]
        proper_root = Node.build_tree([1, [2, 9, [8, 5, 5, 2], 8], [3, 4, [5, 6, 7], [2, 5, 9]], 7])
        proper_node = Node.build_tree([7])

        tested_node.replace_with(replacement)
        self.fully_assert(tested_node, tested_root, proper_node, proper_root)

    def test_replace_node_with_alien_subtree(self):
        tested_root = Node.build_tree([1, [2, 9, [8, 5, 7, 2], 8], 5, [3, 4, [5, 6, 7], [2, 5, 9]], 7])
        tested_node = tested_root.successors[0].successors[1]
        alien_root = Node.build_tree([5, 3, [2, 6, 9, 0], 4, [2, 0, [1, 2, 4], 4]])
        replacement = alien_root.successors[3].successors[1]

        proper_root = Node.build_tree([1, [2, 9, [1, 2, 4], 8], 5, [3, 4, [5, 6, 7], [2, 5, 9]], 7])
        proper_node = Node.build_tree([8, 5, 7, 2])
        proper_alien_root = Node.build_tree([5, 3, [2, 6, 9, 0], 4, [2, 0, 4]])

        tested_node.replace_with(replacement)
        self.fully_assert(tested_node, tested_root, proper_node, proper_root)
        self.assertTrue(is_subtree_valid(alien_root))
        self.assertEqual(proper_alien_root, alien_root)

    def test_closing_replace(self):
        tested_root = Node.build_tree([1, [2, 9, [8, 5, 7, 2], 8], 5, [3, 4, [5, 6, 7], [2, 5, 9]], 7])
        tested_node = tested_root.successors[0]
        replacement = tested_root.successors[0].successors[1]
        proper_root = Node.build_tree([1, [8, 5, 7, 2], 5, [3, 4, [5, 6, 7], [2, 5, 9]], 7])
        proper_node = Node.build_tree([2, 9, 8])

        tested_node.replace_with(replacement)
        self.fully_assert(tested_node, tested_root, proper_node, proper_root)


    def fully_assert(self, tested_node: Node, tested_root: Node, proper_node: Node, proper_root: Node):
        self.assertEqual(None, tested_node.parent)
        self.assertTrue(is_subtree_valid(tested_root))
        self.assertEqual(proper_root, tested_root)
        self.assertEqual(proper_node, tested_node)


class TestNodeSwapWith(unittest.TestCase):
    def test_swap_nodes_inside_tree(self):
        tested_root = Node.build_tree([1, [2, 9, [8, 5, 7, 2], 8], 5, [3, 4, [5, 6, 7], [2, 5, 9]], 7])
        tested_node = tested_root.successors[0]
        partner = tested_root.successors[2].successors[1]
        proper_root = Node.build_tree([1, [5, 6, 7], 5, [3, 4, [2, 9, [8, 5, 7, 2], 8], [2, 5, 9]], 7])

        tested_node.swap_with(partner)
        self.assertTrue(is_subtree_valid(tested_root))
        self.assertEqual(tested_root, proper_root)

    def test_swap_nodes_between_trees(self):
        tested_root = Node.build_tree([1, [2, 9, [8, 5, 7, 2], 8], 5, [3, 4, [5, 6, 7], [2, 5, 9]], 7])
        tested_node = tested_root.successors[0].successors[1]
        alien_root = Node.build_tree([5, 3, [2, 6, 9, 0], 4, [2, 0, [1, 2, 4], 4]])
        partner = alien_root.successors[3].successors[1]

        proper_root = Node.build_tree([1, [2, 9, [1, 2, 4], 8], 5, [3, 4, [5, 6, 7], [2, 5, 9]], 7])
        proper_alien_root = Node.build_tree([5, 3, [2, 6, 9, 0], 4, [2, 0, [8, 5, 7, 2], 4]])

        tested_node.swap_with(partner)
        self.assertTrue(is_subtree_valid(tested_root))
        self.assertTrue(is_subtree_valid(alien_root))
        self.assertEqual(tested_root, proper_root)
        self.assertEqual(alien_root, proper_alien_root)

    def test_closing_swap_node_down(self):
        tested_root = Node.build_tree([1, [2, 9, [8, 5, 7, 2], 8], 5, [3, 4, [5, 6, 7], [2, 5, 9]], 7])
        tested_node = tested_root.successors[0]
        partner = tested_root.successors[0].successors[1]
        with self.assertRaises(Node.ClosingTransition):
            tested_node.swap_with(partner)

    def test_closing_swap_node_up(self):
        tested_root = Node.build_tree([1, [2, 9, [8, 5, 7, 2], 8], 5, [3, 4, [5, 6, 7], [2, 5, 9]], 7])
        tested_node = tested_root.successors[0].successors[1]
        partner = tested_root.successors[0]
        with self.assertRaises(Node.ClosingTransition):
            tested_node.swap_with(partner)


class TestNodeReadOnlyMethods(unittest.TestCase):
    def test_by_creation(self):
        root = Node.build_tree([1, [2, 9, [8, 5, 7, 2], 8], 5, [3, 4, [5, 6, 7], [2, 5, 9]], 7])
        inner_node = root.successors[0].successors[1]
        leaf = root.successors[2].successors[1].successors[1]
        free_node = Node.build_tree([1])

        self.assertTrue(root.is_root())
        self.assertFalse(inner_node.is_root())
        self.assertFalse(leaf.is_root())
        self.assertTrue(free_node.is_root())

        self.assertTrue(root.is_parent())
        self.assertTrue(inner_node.is_parent())
        self.assertFalse(leaf.is_parent())
        self.assertFalse(free_node.is_parent())

        self.assertTrue(root.is_ancestor(inner_node))
        self.assertFalse(inner_node.is_ancestor(leaf))

    def test_after_swapping(self):
        root = Node.build_tree([1, [2, 9, [8, 5, 7, 2], 8], 5, [3, 4, [5, 6, 7], [2, 5, 9]], 7])
        inner_node = root.successors[0].successors[1]
        leaf = root.successors[2].successors[1].successors[1]
        ancestor = root.successors[0]

        inner_node.swap_with(leaf)
        self.assertFalse(inner_node.is_root())
        self.assertFalse(leaf.is_root())
        self.assertTrue(inner_node.is_parent())
        self.assertFalse(leaf.is_parent())

        self.assertTrue(ancestor.is_ancestor(leaf))

    def test_after_replacement(self):
        root = Node.build_tree([1, [2, 9, [8, 5, 7, 2], 8], 5, [3, 4, [5, 6, 7], [2, 5, 9]], 7])
        inner_node = root.successors[0].successors[1]

        root.replace_with(inner_node)
        self.assertTrue(root.is_root())
        self.assertTrue(inner_node.is_root())
        self.assertTrue(root.is_parent())
        self.assertTrue(inner_node.is_parent())

        self.assertFalse(root.is_ancestor(inner_node))


# class TestForestCreateRoot(unittest.TestCase):
#     def test_create_first_root(self):
#         tested_forest = Forest.build_forest()
#         proper_forest = Forest.build_forest([5])
#         tested_forest.create_root(5)
#         self.assertEqual(proper_forest, tested_forest)




class TestTree(unittest.TestCase):
    pass
    # TODO: Test tree-specific content and some forest functions on tree

if __name__ == '__main__':
    unittest.main()
