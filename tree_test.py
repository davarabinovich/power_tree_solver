
import unittest
from tree import *

# TODO: Check, that any exception cancels all modifications!!!
def convert_tree_list_to_flat_list(forest_list):
    if type(forest_list) == list:
        flat_list = [forest_list[0]]
        forest_list = forest_list[1:]
        for successor in forest_list:
            suffix = convert_tree_list_to_flat_list(successor)
            if type(suffix) == list:
                flat_list += suffix
            else:
                flat_list.append(suffix)
        return flat_list
    return forest_list

def convert_forest_list_to_flat_list(*argv):
    flat_list = []
    for root in argv:
        flat_list += convert_tree_list_to_flat_list(root)
    return flat_list

def is_subtree_valid(root: Node):
    for successor in root.successors:
        if successor.parent != root:
            return False
        is_subtree_valid(successor)
    return True

def is_forest_valid(forest: Forest):
    for root in forest.roots:
        if not is_forest_tree_valid(root, forest):
            return False
    return True

def is_forest_tree_valid(root: Forest.ForestNode, forest: Forest):
    if root.get_forest_ref() != forest:
        return False

    for successor in root.successors:
        if successor.parent != root:
            return False
        is_subtree_valid(successor)
    return True

# TODO: Make input lists as constants
# TODO: Check cases with several exceptions during one method call
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
        proper_alien_root = Node.build_tree([0,
                                             [1, [2, 9, [8, 5, 7, 2], 8], 5, [3, 4, [5, [6, 9, 0], 7], [2, 5, 9]], 7]])

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
        tested_root_copy = Node.build_tree([1, [2, 9], 5, [3, 4, [5, [6, 9, 0]], [2, 5, 9]], 7])
        tested_node = tested_root.successors[2]
        tested_parent = tested_root.successors[2].successors[1].successors[0].successors[1]

        with self.assertRaises(Node.ClosingTransition):
            tested_node.connect_to(tested_parent)
        self.assertEqual(tested_root, tested_root_copy)


    def test_closing_connection_subtree_to_subtree(self):
        tested_root = Node.build_tree([1, [2, 9], 5, [3, 4, [5, [6, 9, 0]], [2, 5, 9]], 7])
        tested_root_copy = Node.build_tree([1, [2, 9], 5, [3, 4, [5, [6, 9, 0]], [2, 5, 9]], 7])
        tested_node = tested_root.successors[2]
        tested_parent = tested_root.successors[2].successors[1].successors[0]

        with self.assertRaises(Node.ClosingTransition):
            tested_node.connect_to(tested_parent)
        self.assertEqual(tested_root, tested_root_copy)

    def test_closing_connection_root_to_leaf(self):
        tested_root = Node.build_tree([1, [2, 9], 5, [3, 4, [5, [6, 9, 0]], [2, 5, 9]], 7])
        tested_root_copy = Node.build_tree([1, [2, 9], 5, [3, 4, [5, [6, 9, 0]], [2, 5, 9]], 7])
        tested_parent = tested_root.successors[2].successors[1].successors[0].successors[1]

        with self.assertRaises(Node.ClosingTransition):
            tested_root.connect_to(tested_parent)
        self.assertEqual(tested_root, tested_root_copy)

    def test_closing_connection_root_to_subtree(self):
        tested_root = Node.build_tree([1, [2, 9], 5, [3, 4, [5, [6, 9, 0]], [2, 5, 9]], 7])
        tested_root_copy = Node.build_tree([1, [2, 9], 5, [3, 4, [5, [6, 9, 0]], [2, 5, 9]], 7])
        tested_parent = tested_root.successors[2].successors[1].successors[0]

        with self.assertRaises(Node.ClosingTransition):
            tested_root.connect_to(tested_parent)
        self.assertEqual(tested_root, tested_root_copy)


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
        tested_root_copy = Node.build_tree([1, [2, 9, [8, 5, 7, 2], 8], 5, [3, 4, [5, 6, 7], [2, 5, 9]], 7])
        tested_node = tested_root.successors[0]
        partner = tested_root.successors[0].successors[1]

        with self.assertRaises(Node.ClosingTransition):
            tested_node.swap_with(partner)
        self.assertEqual(tested_root, tested_root_copy)

    def test_closing_swap_node_up(self):
        tested_root = Node.build_tree([1, [2, 9, [8, 5, 7, 2], 8], 5, [3, 4, [5, 6, 7], [2, 5, 9]], 7])
        tested_root_copy = Node.build_tree([1, [2, 9, [8, 5, 7, 2], 8], 5, [3, 4, [5, 6, 7], [2, 5, 9]], 7])
        tested_node = tested_root.successors[0].successors[1]
        partner = tested_root.successors[0]

        with self.assertRaises(Node.ClosingTransition):
            tested_node.swap_with(partner)
        self.assertEqual(tested_root, tested_root_copy)


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

        self.assertFalse(root.is_successor())
        self.assertTrue(inner_node.is_successor())
        self.assertTrue(leaf.is_successor())
        self.assertFalse(free_node.is_successor())

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
        self.assertTrue(inner_node.is_successor())
        self.assertTrue(leaf.is_successor())

        self.assertTrue(inner_node.is_parent())
        self.assertFalse(leaf.is_parent())
        self.assertTrue(ancestor.is_ancestor(leaf))

    def test_after_replacement(self):
        root = Node.build_tree([1, [2, 9, [8, 5, 7, 2], 8], 5, [3, 4, [5, 6, 7], [2, 5, 9]], 7])
        inner_node = root.successors[0].successors[1]
        root.replace_with(inner_node)

        self.assertTrue(root.is_root())
        self.assertTrue(inner_node.is_root())
        self.assertFalse(root.is_successor())
        self.assertFalse(inner_node.is_successor())

        self.assertTrue(root.is_parent())
        self.assertTrue(inner_node.is_parent())
        self.assertFalse(root.is_ancestor(inner_node))


class TestNodeIteration(unittest.TestCase):
    def test_iteration_by_alone_node(self):
        tested_root = Node.build_tree([1])
        proper_root_flat_view = convert_tree_list_to_flat_list([1])
        tested_root_flat_view = []
        for node in tested_root:
            tested_root_flat_view.append(node.content)
        self.assertEqual(tested_root_flat_view, proper_root_flat_view)

    def test_iteration_by_list(self):
        tested_root = Node.build_tree([1, [2, [8, 5]]])
        proper_root_flat_view = convert_tree_list_to_flat_list([1, [2, [8, 5]]])
        tested_root_flat_view = []
        for node in tested_root:
            tested_root_flat_view.append(node.content)
        self.assertEqual(tested_root_flat_view, proper_root_flat_view)

    def test_iteration_by_simple_tree(self):
        tested_root = Node.build_tree([1, 2, 9, 8])
        proper_root_flat_view = convert_tree_list_to_flat_list([1, 2, 9, 8])
        tested_root_flat_view = []
        for node in tested_root:
            tested_root_flat_view.append(node.content)
        self.assertEqual(tested_root_flat_view, proper_root_flat_view)

    def test_iteration_by_complex_tree(self):
        tested_root = Node.build_tree([1, [2, 9, [8, 5, 7, 2], 8], 5, [3, 4, [5, 6, 7], [2, 5, 9]], 7])
        proper_root_flat_view = convert_tree_list_to_flat_list([1, [2, 9, [8, 5, 7, 2], 8],
                                                                5, [3, 4, [5, 6, 7], [2, 5, 9]], 7])
        tested_root_flat_view = []
        for node in tested_root:
            tested_root_flat_view.append(node.content)
        self.assertEqual(tested_root_flat_view, proper_root_flat_view)

class TestNodeCalcSubtreeWidth(unittest.TestCase):
    def test_calc_alone_node_width(self):
        tested_root = Node.build_tree([1])
        result = tested_root.calc_subtree_width()
        proper_result = 0
        self.assertEqual(proper_result, result)

    def test_calc_vertical_subtree_width(self):
        tested_root = Node.build_tree([1, [2, [3, [4, [5, 6]]]]])
        result = tested_root.calc_subtree_width()
        proper_result = 0
        self.assertEqual(proper_result, result)

    def test_calc_equally_spread_subtree_width(self):
        tested_root = Node.build_tree([1, [2, 3, 4, 5], [6, 7, 8, 9], [0, 1, 2, 3]])
        result = tested_root.calc_subtree_width()
        proper_result = 8
        self.assertEqual(proper_result, result)

    def test_calc_right_skewed_subtree_width(self):
        tested_root = Node.build_tree([1, 2, [6, 7], [0, 1, 2, 3]])
        result = tested_root.calc_subtree_width()
        proper_result = 4
        self.assertEqual(proper_result, result)

    def test_calc_left_skewed_subtree_width(self):
        tested_root = Node.build_tree([1, [2, 3, 4, 5], [6, 7], 0])
        result = tested_root.calc_subtree_width()
        proper_result = 4
        self.assertEqual(proper_result, result)


class TestNodeCalcSubtreeDepth(unittest.TestCase):
    def test_calc_alone_node_depth(self):
        tested_root = Node.build_tree([1])
        result = tested_root.calc_subtree_depth()
        proper_result = 0
        self.assertEqual(proper_result, result)

    def test_calc_vertical_subtree_depth(self):
        tested_root = Node.build_tree([1, [2, [3, [4, [5, [6, [7, [8, [9, 0, 1], 2], 3], 4], 5], 6], 7], 8], 9])
        result = tested_root.calc_subtree_depth()
        proper_result = 9
        self.assertEqual(proper_result, result)

    def test_calc_equally_spread_subtree_depth(self):
        tested_root = Node.build_tree([1, [2, 3, 4, 5], [6, 7, 8, 9], [0, 1, 2, 3]])
        result = tested_root.calc_subtree_depth()
        proper_result = 2
        self.assertEqual(proper_result, result)

    def test_calc_right_skewed_subtree_depth(self):
        tested_root = Node.build_tree([1, 2, [6, 7], [0, 1, 2, 3]])
        result = tested_root.calc_subtree_depth()
        proper_result = 2
        self.assertEqual(proper_result, result)

    def test_calc_left_skewed_subtree_depth(self):
        tested_root = Node.build_tree([1, [2, 3, 4, 5], [6, 7], 0])
        result = tested_root.calc_subtree_depth()
        proper_result = 2
        self.assertEqual(proper_result, result)

# TODO: Need to test index_by_parent

# TODO: Check equivalency of work of two different methods where it's possible \
#       (for example add_leaf to None and create_root)
class TestForestCreateRoot(unittest.TestCase):
    def test_create_first_root(self):
        tested_forest = Forest.build_forest()
        proper_forest = Forest.build_forest([5])
        tested_forest.create_root(5)
        self.assertTrue(is_forest_valid(tested_forest))
        self.assertEqual(proper_forest, tested_forest)

    def test_create_additional_roots(self):
        tested_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        proper_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]], [4])
        tested_forest.create_root(4)
        self.assertTrue(is_forest_valid(tested_forest))
        self.assertEqual(proper_forest, tested_forest)


class TestForestAddLeaf(unittest.TestCase):
    def test_add_leaf_to_parent(self):
        tested_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        proper_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9, 4]])
        parent = tested_forest.roots[2].successors[2]
        tested_forest.add_leaf(parent, 4)
        self.assertTrue(is_forest_valid(tested_forest))
        self.assertEqual(proper_forest, tested_forest)

    def test_add_leaf_to_leaf(self):
        tested_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        proper_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5, 4], [3, 4, [5, 6, 7], [2, 5, 9]])
        parent = tested_forest.roots[1]
        tested_forest.add_leaf(parent, 4)
        self.assertTrue(is_forest_valid(tested_forest))
        self.assertEqual(proper_forest, tested_forest)

    def test_add_leaf_to_alien_node(self):
        tested_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        tested_forest_copy = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        alien_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        parent = alien_forest.roots[2].successors[2]

        with self.assertRaises(Forest.AlienNode):
            tested_forest.add_leaf(parent, 4)
        self.assertEqual(tested_forest, tested_forest_copy)


class TestForestInsertNodeBefore(unittest.TestCase):
    def test_insert_node_before_root(self):
        tested_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        proper_forest = Forest.build_forest([0, [2, 9, [8, 5, 7, 2], 8]], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        tested_node = tested_forest.roots[0]

        tested_forest.insert_node_before(tested_node, 0)
        self.assertTrue(is_forest_valid(tested_forest))
        self.assertEqual(proper_forest, tested_forest)

    def test_insert_node_before_inner_node(self):
        tested_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        proper_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, [0, 4], [5, 6, 7], [2, 5, 9]])
        tested_node = tested_forest.roots[2].successors[0]

        tested_forest.insert_node_before(tested_node, 0)
        self.assertTrue(is_forest_valid(tested_forest))
        self.assertEqual(proper_forest, tested_forest)

    def insert_node_before_alien_node(self):
        tested_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        tested_forest_copy = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        alien_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        successor = alien_forest.roots[2].successors[2]

        with self.assertRaises(Forest.AlienNode):
            tested_forest.insert_node_before(successor, 4)
        self.assertEqual(tested_forest, tested_forest_copy)


class TestForestInsertNodeAfter(unittest.TestCase):
    def test_insert_node_after_inner_node(self):
        tested_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        proper_forest = Forest.build_forest([2, 9, [8, [0, 5, 7, 2]], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        tested_node = tested_forest.roots[0].successors[1]

        tested_forest.insert_node_after(tested_node, 0)
        self.assertTrue(is_forest_valid(tested_forest))
        self.assertEqual(proper_forest, tested_forest)

    def insert_node_after_alien_node(self):
        tested_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        tested_forest_copy = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        alien_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        parent = alien_forest.roots[2].successors[2]

        with self.assertRaises(Forest.AlienNode):
            tested_forest.insert_node_after(parent, 4)
        self.assertEqual(tested_forest, tested_forest_copy)


class TestForestMoveNode(unittest.TestCase):
    def test_move_root_with_successors_to_inner_node(self):
        tested_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        proper_forest = Forest.build_forest([5], [3, 4, [5, 6, 7], [2, 5, 9], 2], [9], [8, 5, 7, 2], [8])
        tested_node = tested_forest.roots[0]
        tested_parent = tested_forest.roots[2]

        tested_forest.move_node(tested_node, tested_parent)
        self.assertTrue(is_forest_valid(tested_forest))
        self.assertEqual(proper_forest, tested_forest)

    def test_move_inner_node_to_leaf(self):
        tested_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        proper_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5, 3], [4], [5, 6, 7], [2, 5, 9])
        tested_node = tested_forest.roots[2]
        tested_parent = tested_forest.roots[1]

        tested_forest.move_node(tested_node, tested_parent)
        self.assertTrue(is_forest_valid(tested_forest))
        self.assertEqual(proper_forest, tested_forest)

    def test_move_leaf_to_inner_node(self):
        tested_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        proper_forest = Forest.build_forest([2, 9, [8, 5, 7, 2, 5], 8], [5], [3, 4, [5, 6, 7], [2, 9]])
        tested_node = tested_forest.roots[2].successors[2].successors[0]
        tested_parent = tested_forest.roots[0].successors[1]

        tested_forest.move_node(tested_node, tested_parent)
        self.assertTrue(is_forest_valid(tested_forest))
        self.assertEqual(proper_forest, tested_forest)

    def test_closing_move_ancestor_below(self):
        tested_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        proper_forest = Forest.build_forest([2, 9, 8, 5, [7, 8], 2], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        tested_node = tested_forest.roots[0].successors[1]
        tested_parent = tested_forest.roots[0].successors[1].successors[1]

        tested_forest.move_node(tested_node, tested_parent)
        self.assertTrue(is_forest_valid(tested_forest))
        self.assertEqual(proper_forest, tested_forest)

    def test_move_descendant_above(self):
        tested_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        proper_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 7], [2, 5, 9], 6])
        tested_node = tested_forest.roots[2].successors[1].successors[0]
        tested_parent = tested_forest.roots[2]

        tested_forest.move_node(tested_node, tested_parent)
        self.assertTrue(is_forest_valid(tested_forest))
        self.assertEqual(proper_forest, tested_forest)

    def test_move_node_to_alien_node(self):
        tested_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        tested_forest_copy = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        tested_node = tested_forest.roots[2].successors[1].successors[0]

        alien_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        alien_forest_copy = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        parent = alien_forest.roots[2].successors[2]

        with self.assertRaises(Forest.AlienNode):
            tested_forest.move_node(tested_node, parent)
        self.assertEqual(tested_forest, tested_forest_copy)
        self.assertEqual(alien_forest, alien_forest_copy)

    def test_move_alien_node_to_node(self):
        tested_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        tested_forest_copy = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        parent = tested_forest.roots[2].successors[2]

        alien_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        alien_forest_copy = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        tested_node = alien_forest.roots[2].successors[1].successors[0]

        with self.assertRaises(Forest.AlienNode):
            tested_forest.move_node(tested_node, parent)
        self.assertEqual(tested_forest, tested_forest_copy)
        self.assertEqual(alien_forest, alien_forest_copy)


class TestForestMoveSubtree(unittest.TestCase):
    def test_move_root_to_root(self):
        tested_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        proper_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8, [3, 4, [5, 6, 7], [2, 5, 9]]], [5])
        tested_node = tested_forest.roots[2]
        tested_parent = tested_forest.roots[0]

        tested_forest.move_subtree(tested_node, tested_parent)
        self.assertTrue(is_forest_valid(tested_forest))
        self.assertEqual(proper_forest, tested_forest)

    def test_move_root_to_leaf(self):
        tested_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        proper_forest = Forest.build_forest([5], [3, [4, [2, 9, [8, 5, 7, 2], 8]], [5, 6, 7], [2, 5, 9]])
        tested_node = tested_forest.roots[0]
        tested_parent = tested_forest.roots[2].successors[0]

        tested_forest.move_subtree(tested_node, tested_parent)
        self.assertTrue(is_forest_valid(tested_forest))
        self.assertEqual(proper_forest, tested_forest)

    def test_move_subtree_to_inner_node(self):
        tested_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        proper_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [2, 5, 9, [5, 6, 7]]])
        tested_node = tested_forest.roots[2].successors[1]
        tested_parent = tested_forest.roots[2].successors[2]

        tested_forest.move_subtree(tested_node, tested_parent)
        self.assertTrue(is_forest_valid(tested_forest))
        self.assertEqual(proper_forest, tested_forest)

    def test_move_leaf_above(self):
        tested_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        proper_forest = Forest.build_forest([2, 9, [8, 5, 7], 8, 2], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        tested_node = tested_forest.roots[0].successors[1].successors[2]
        tested_parent = tested_forest.roots[0]

        tested_forest.move_subtree(tested_node, tested_parent)
        self.assertTrue(is_forest_valid(tested_forest))
        self.assertEqual(proper_forest, tested_forest)

    def test_closing_move_root(self):
        tested_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        tested_forest_copy = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        tested_node = tested_forest.roots[0]
        tested_parent = tested_forest.roots[0].successors[0]

        with self.assertRaises(Node.ClosingTransition):
            tested_forest.move_subtree(tested_node, tested_parent)
        self.assertEqual(tested_forest, tested_forest_copy)

    def test_move_subtree_to_alien_node(self):
        tested_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        tested_forest_copy = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        alien_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        tested_node = tested_forest.roots[2].successors[1].successors[0]
        parent = alien_forest.roots[2].successors[2]

        with self.assertRaises(Forest.AlienNode):
            tested_forest.move_subtree(tested_node, parent)
        self.assertEqual(tested_forest, tested_forest_copy)

    def test_move_alien_subtree_to_node(self):
        tested_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        tested_forest_copy = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        parent = tested_forest.roots[2].successors[2]

        alien_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        alien_forest_copy = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        tested_node = alien_forest.roots[2].successors[1].successors[0]

        with self.assertRaises(Forest.AlienNode):
            tested_forest.move_subtree(tested_node, parent)
        self.assertEqual(tested_forest, tested_forest_copy)
        self.assertEqual(alien_forest, alien_forest_copy)


class TestForestFreeLeafage(unittest.TestCase):
    def test_free_roots_leafage(self):
        tested_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        proper_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3], [4], [5, 6, 7], [2, 5, 9])
        tested_node = tested_forest.roots[2]

        tested_forest.free_leafage(tested_node)
        self.assertTrue(is_forest_valid(tested_forest))
        self.assertEqual(proper_forest, tested_forest)

    def test_free_inner_nodes_leafage(self):
        tested_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        proper_forest = Forest.build_forest([2, 9, 8, 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]], [5], [7], [2])
        tested_node = tested_forest.roots[0].successors[1]

        tested_forest.free_leafage(tested_node)
        self.assertTrue(is_forest_valid(tested_forest))
        self.assertEqual(proper_forest, tested_forest)

    def test_free_leafs_leafage(self):
        tested_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        proper_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        tested_node = tested_forest.roots[2].successors[1].successors[0]

        tested_forest.free_leafage(tested_node)
        self.assertTrue(is_forest_valid(tested_forest))
        self.assertEqual(proper_forest, tested_forest)

    def test_free_root_leafs_leafage(self):
        tested_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        proper_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        tested_node = tested_forest.roots[1]

        tested_forest.free_leafage(tested_node)
        self.assertTrue(is_forest_valid(tested_forest))
        self.assertEqual(proper_forest, tested_forest)

    def test_free_alien_nodes_leafage(self):
        tested_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        tested_forest_copy = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        alien_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        alien_forest_copy = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        tested_node = alien_forest.roots[2].successors[1].successors[0]

        with self.assertRaises(Forest.AlienNode):
            tested_forest.free_leafage(tested_node)
        self.assertEqual(tested_forest, tested_forest_copy)
        self.assertEqual(alien_forest, alien_forest_copy)


class TestForestFreeLeaf(unittest.TestCase):
    def test_free_root_parent(self):
        tested_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        tested_forest_copy = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        tested_node = tested_forest.roots[2]

        with self.assertRaises(Forest.NotLeaf):
            tested_forest.free_leaf(tested_node)
        self.assertEqual(tested_forest, tested_forest_copy)

    def test_free_inner_parent(self):
        tested_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        tested_forest_copy = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        tested_node = tested_forest.roots[0].successors[1]

        with self.assertRaises(Forest.NotLeaf):
            tested_forest.free_leaf(tested_node)
        self.assertEqual(tested_forest, tested_forest_copy)

    def test_free_leaf(self):
        tested_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        proper_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 7], [2, 5, 9]], [6])
        tested_node = tested_forest.roots[2].successors[1].successors[0]

        tested_forest.free_leaf(tested_node)
        self.assertTrue(is_forest_valid(tested_forest))
        self.assertEqual(proper_forest, tested_forest)

    def test_free_root_leaf(self):
        tested_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        proper_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        tested_node = tested_forest.roots[1]

        tested_forest.free_leaf(tested_node)
        self.assertTrue(is_forest_valid(tested_forest))
        self.assertEqual(proper_forest, tested_forest)

    def test_free_alien_leaf(self):
        tested_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        tested_forest_copy = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        alien_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        alien_forest_copy = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        tested_node = alien_forest.roots[2].successors[1].successors[0]

        with self.assertRaises(Forest.AlienNode):
            tested_forest.free_leaf(tested_node)
        self.assertEqual(tested_forest, tested_forest_copy)
        self.assertEqual(alien_forest, alien_forest_copy)


class TestForestFreeNode(unittest.TestCase):
    def test_free_root(self):
        tested_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        proper_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3], [4], [5, 6, 7], [2, 5, 9])
        tested_node = tested_forest.roots[2]

        tested_forest.free_node(tested_node)
        self.assertTrue(is_forest_valid(tested_forest))
        self.assertEqual(proper_forest, tested_forest)

    def test_free_inner_node(self):
        tested_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        proper_forest = Forest.build_forest([2, 9, 8, 5, 7, 2], [5], [3, 4, [5, 6, 7], [2, 5, 9]], [8])
        tested_node = tested_forest.roots[0].successors[1]

        tested_forest.free_node(tested_node)
        self.assertTrue(is_forest_valid(tested_forest))
        self.assertEqual(proper_forest, tested_forest)

    def test_free_leaf(self):
        tested_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        proper_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 7], [2, 5, 9]], [6])
        tested_node = tested_forest.roots[2].successors[1].successors[0]

        tested_forest.free_node(tested_node)
        self.assertTrue(is_forest_valid(tested_forest))
        self.assertEqual(proper_forest, tested_forest)

    def test_free_root_leaf(self):
        tested_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        proper_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        tested_node = tested_forest.roots[1]

        tested_forest.free_node(tested_node)
        self.assertTrue(is_forest_valid(tested_forest))
        self.assertEqual(proper_forest, tested_forest)

    def test_free_alien_node(self):
        tested_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        tested_forest_copy = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        alien_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        alien_forest_copy = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        tested_node = alien_forest.roots[2].successors[1].successors[0]

        with self.assertRaises(Forest.AlienNode):
            tested_forest.free_node(tested_node)
        self.assertEqual(tested_forest, tested_forest_copy)
        self.assertEqual(alien_forest, alien_forest_copy)


class TestForestFreeSubtree(unittest.TestCase):
    def test_free_root(self):
        tested_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        proper_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        tested_node = tested_forest.roots[2]

        tested_forest.free_subtree(tested_node)
        self.assertTrue(is_forest_valid(tested_forest))
        self.assertEqual(proper_forest, tested_forest)

    def test_free_subtree(self):
        tested_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        proper_forest = Forest.build_forest([2, 9, 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]], [8, 5, 7, 2])
        tested_node = tested_forest.roots[0].successors[1]

        tested_forest.free_subtree(tested_node)
        self.assertTrue(is_forest_valid(tested_forest))
        self.assertEqual(proper_forest, tested_forest)

    def test_free_leaf(self):
        tested_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        proper_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 7], [2, 5, 9]], [6])
        tested_node = tested_forest.roots[2].successors[1].successors[0]

        tested_forest.free_subtree(tested_node)
        self.assertTrue(is_forest_valid(tested_forest))
        self.assertEqual(proper_forest, tested_forest)

    def test_free_root_leaf(self):
        tested_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        proper_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        tested_node = tested_forest.roots[1]

        tested_forest.free_subtree(tested_node)
        self.assertTrue(is_forest_valid(tested_forest))
        self.assertEqual(proper_forest, tested_forest)

    def test_free_alien_subtree(self):
        tested_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        tested_forest_copy = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        alien_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        alien_forest_copy = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        tested_node = alien_forest.roots[2].successors[1].successors[0]

        with self.assertRaises(Forest.AlienNode):
            tested_forest.free_subtree(tested_node)
        self.assertEqual(tested_forest, tested_forest_copy)
        self.assertEqual(alien_forest, alien_forest_copy)

class TestForestDeleteLeafage(unittest.TestCase):
    def test_delete_roots_leafage(self):
        tested_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        proper_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3])
        tested_node = tested_forest.roots[2]

        tested_forest.delete_leafage(tested_node)
        self.assertTrue(is_forest_valid(tested_forest))
        self.assertEqual(proper_forest, tested_forest)

    def test_free_inner_nodes_leafage(self):
        tested_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        proper_forest = Forest.build_forest([2, 9, 8, 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        tested_node = tested_forest.roots[0].successors[1]

        tested_forest.delete_leafage(tested_node)
        self.assertTrue(is_forest_valid(tested_forest))
        self.assertEqual(proper_forest, tested_forest)

    def test_free_leafs_leafage(self):
        tested_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        proper_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        tested_node = tested_forest.roots[2].successors[1].successors[0]

        tested_forest.delete_leafage(tested_node)
        self.assertTrue(is_forest_valid(tested_forest))
        self.assertEqual(proper_forest, tested_forest)

    def test_free_root_leafs_leafage(self):
        tested_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        proper_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        tested_node = tested_forest.roots[1]

        tested_forest.delete_leafage(tested_node)
        self.assertTrue(is_forest_valid(tested_forest))
        self.assertEqual(proper_forest, tested_forest)

    def test_free_alien_nodes_leafage(self):
        tested_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        tested_forest_copy = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        alien_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        alien_forest_copy = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        tested_node = alien_forest.roots[2].successors[1].successors[0]

        with self.assertRaises(Forest.AlienNode):
            tested_forest.delete_leafage(tested_node)
        self.assertEqual(tested_forest, tested_forest_copy)
        self.assertEqual(alien_forest, alien_forest_copy)


class TestForestDeleteLeaf(unittest.TestCase):
    def test_delete_root_parent(self):
        tested_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        tested_forest_copy = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        tested_node = tested_forest.roots[2]

        with self.assertRaises(Forest.NotLeaf):
            tested_forest.delete_leaf(tested_node)
        self.assertEqual(tested_forest, tested_forest_copy)
#
    def test_delete_inner_parent(self):
        tested_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        tested_forest_copy = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        tested_node = tested_forest.roots[0].successors[1]

        with self.assertRaises(Forest.NotLeaf):
            tested_forest.delete_leaf(tested_node)
        self.assertEqual(tested_forest, tested_forest_copy)

    def test_delete_leaf(self):
        tested_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        proper_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 7], [2, 5, 9]])
        tested_node = tested_forest.roots[2].successors[1].successors[0]

        tested_forest.delete_leaf(tested_node)
        self.assertTrue(is_forest_valid(tested_forest))
        self.assertEqual(proper_forest, tested_forest)
#
    def test_delete_root_leaf(self):
        tested_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        proper_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [3, 4, [5, 6, 7], [2, 5, 9]])
        tested_node = tested_forest.roots[1]

        tested_forest.delete_leaf(tested_node)
        self.assertTrue(is_forest_valid(tested_forest))
        self.assertEqual(proper_forest, tested_forest)
#
    def test_delete_alien_leaf(self):
        tested_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        tested_forest_copy = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        alien_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        alien_forest_copy = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        tested_node = alien_forest.roots[2].successors[1].successors[0]

        with self.assertRaises(Forest.AlienNode):
            tested_forest.delete_leaf(tested_node)
        self.assertEqual(tested_forest, tested_forest_copy)
        self.assertEqual(alien_forest, alien_forest_copy)


class TestForestCutNode(unittest.TestCase):
    def test_cut_root(self):
        tested_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        proper_forest = Forest.build_forest([5], [3, 4, [5, 6, 7], [2, 5, 9]], [9], [8, 5, 7, 2], [8])
        tested_node = tested_forest.roots[0]

        tested_forest.cut_node(tested_node)
        self.assertTrue(is_forest_valid(tested_forest))
        self.assertEqual(proper_forest, tested_forest)

    def test_cut_inner_node(self):
        tested_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        proper_forest = Forest.build_forest([2, 9, 8, 5, 7, 2], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        tested_node = tested_forest.roots[0].successors[1]

        tested_forest.cut_node(tested_node)
        self.assertTrue(is_forest_valid(tested_forest))
        self.assertEqual(proper_forest, tested_forest)
#
    def test_cut_leaf(self):
        tested_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        proper_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 7], [2, 5, 9]])
        tested_node = tested_forest.roots[2].successors[1].successors[0]

        tested_forest.cut_node(tested_node)
        self.assertTrue(is_forest_valid(tested_forest))
        self.assertEqual(proper_forest, tested_forest)

    def test_cut_root_leaf(self):
        tested_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        proper_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [3, 4, [5, 6, 7], [2, 5, 9]])
        tested_node = tested_forest.roots[1]

        tested_forest.cut_node(tested_node)
        self.assertTrue(is_forest_valid(tested_forest))
        self.assertEqual(proper_forest, tested_forest)

    def test_cut_alien_node(self):
        tested_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        tested_forest_copy = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        alien_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        alien_forest_copy = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        tested_node = alien_forest.roots[2].successors[1].successors[0]

        with self.assertRaises(Forest.AlienNode):
            tested_forest.cut_node(tested_node)
        self.assertEqual(tested_forest, tested_forest_copy)
        self.assertEqual(alien_forest, alien_forest_copy)

    def test_cut_inner_node_replacing_with_children(self):
        tested_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        proper_forest = Forest.build_forest([2, 9, 5, 7, 2, 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        tested_node = tested_forest.roots[0].successors[1]

        tested_forest.cut_node(tested_node, is_needed_to_replace_node_with_successors=True)
        self.assertTrue(is_forest_valid(tested_forest))
        self.assertEqual(proper_forest, tested_forest)


class TestForestDeleteSubtree(unittest.TestCase):
    def test_delete_root(self):
        tested_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        proper_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5])
        tested_node = tested_forest.roots[2]

        tested_forest.delete_subtree(tested_node)
        self.assertTrue(is_forest_valid(tested_forest))
        self.assertEqual(proper_forest, tested_forest)
#
    def test_delete_subtree(self):
        tested_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        proper_forest = Forest.build_forest([2, 9, 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        tested_node = tested_forest.roots[0].successors[1]

        tested_forest.delete_subtree(tested_node)
        self.assertTrue(is_forest_valid(tested_forest))
        self.assertEqual(proper_forest, tested_forest)

    def test_delete_leaf(self):
        tested_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        proper_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 7], [2, 5, 9]])
        tested_node = tested_forest.roots[2].successors[1].successors[0]

        tested_forest.delete_subtree(tested_node)
        self.assertTrue(is_forest_valid(tested_forest))
        self.assertEqual(proper_forest, tested_forest)

    def test_free_root_leaf(self):
        tested_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        proper_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [3, 4, [5, 6, 7], [2, 5, 9]])
        tested_node = tested_forest.roots[1]

        tested_forest.delete_subtree(tested_node)
        self.assertTrue(is_forest_valid(tested_forest))
        self.assertEqual(proper_forest, tested_forest)

    def test_free_alien_subtree(self):
        tested_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        tested_forest_copy = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        alien_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        alien_forest_copy = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        tested_node = alien_forest.roots[2].successors[1].successors[0]

        with self.assertRaises(Forest.AlienNode):
            tested_forest.delete_subtree(tested_node)
        self.assertEqual(tested_forest, tested_forest_copy)
        self.assertEqual(alien_forest, alien_forest_copy)


class TestForestIteration(unittest.TestCase):
    def test_iteration_empty_forest(self):
        tested_forest = Forest()
        proper_forest_flat_view = []
        tested_forest_flat_view = []
        for node in tested_forest:
            tested_forest_flat_view.append(node.content)
        self.assertEqual(tested_forest_flat_view, proper_forest_flat_view)

    def test_iteration_alone_node(self):
        tested_forest = Forest.build_forest([2])
        proper_forest_flat_view = convert_forest_list_to_flat_list([2])
        tested_forest_flat_view = []
        for node in tested_forest:
            tested_forest_flat_view.append(node.content)
        self.assertEqual(tested_forest_flat_view, proper_forest_flat_view)

    def test_iteration_single_list(self):
        tested_forest = Forest.build_forest([2, 3])
        proper_forest_flat_view = convert_forest_list_to_flat_list([2, 3])
        tested_forest_flat_view = []
        for node in tested_forest:
            tested_forest_flat_view.append(node.content)
        self.assertEqual(tested_forest_flat_view, proper_forest_flat_view)

    def test_iteration_single_simple_tree(self):
        tested_forest = Forest.build_forest([2, 3, 4, 5])
        proper_forest_flat_view = convert_forest_list_to_flat_list([2, 3, 4, 5])
        tested_forest_flat_view = []
        for node in tested_forest:
            tested_forest_flat_view.append(node.content)
        self.assertEqual(tested_forest_flat_view, proper_forest_flat_view)

    def test_iteration_singletons_forest(self):
        tested_forest = Forest.build_forest([2], [3])
        proper_forest_flat_view = convert_forest_list_to_flat_list([2], [3])
        tested_forest_flat_view = []
        for node in tested_forest:
            tested_forest_flat_view.append(node.content)
        self.assertEqual(tested_forest_flat_view, proper_forest_flat_view)

    def test_iteration_simple_trees(self):
        tested_forest = Forest.build_forest([2, 3, 4, 5], [6, 7, 8, 9])
        proper_forest_flat_view = convert_forest_list_to_flat_list([2, 3, 4, 5], [6, 7, 8, 9])
        tested_forest_flat_view = []
        for node in tested_forest:
            tested_forest_flat_view.append(node.content)
        self.assertEqual(tested_forest_flat_view, proper_forest_flat_view)

    def test_iteration_forest(self):
        tested_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        proper_forest_flat_view = convert_forest_list_to_flat_list([2, 9, [8, 5, 7, 2], 8],
                                                                   [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        tested_forest_flat_view = []
        for node in tested_forest:
            tested_forest_flat_view.append(node.content)
        self.assertEqual(tested_forest_flat_view, proper_forest_flat_view)
# TODO: Swap expected and actual everywhere
# TODO: Test find root

class TestForestCalcDistance(unittest.TestCase):
    def test_calc_distance_simple_case(self):
        tested_forest = Forest.build_forest([0, [1, 2, 3, 4], 5])
        first = tested_forest.roots[0].successors[0]
        second = tested_forest.roots[0].successors[1]
        result = tested_forest.calc_distance(first, second)
        proper_result = (0, -3)
        self.assertEqual(proper_result, result)

        new_first = second
        new_second = first
        new_result = tested_forest.calc_distance(new_first, new_second)
        new_proper_result = (-proper_result[0], -proper_result[1])
        self.assertEqual(new_proper_result, new_result)

    def test_calc_distance_between_same_root(self):
        tested_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        first = tested_forest.roots[2]
        second = tested_forest.roots[2]
        result = tested_forest.calc_distance(first, second)
        proper_result = (0, 0)
        self.assertEqual(proper_result, result)

        new_first = second
        new_second = first
        new_result = tested_forest.calc_distance(new_first, new_second)
        new_proper_result = (-proper_result[0], -proper_result[1])
        self.assertEqual(new_proper_result, new_result)

    def test_calc_distance_between_same_inner_node(self):
        tested_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        first = tested_forest.roots[0].successors[1]
        second = tested_forest.roots[0].successors[1]
        result = tested_forest.calc_distance(first, second)
        proper_result = (0, 0)
        self.assertEqual(proper_result, result)

        new_first = second
        new_second = first
        new_result = tested_forest.calc_distance(new_first, new_second)
        new_proper_result = (-proper_result[0], -proper_result[1])
        self.assertEqual(new_proper_result, new_result)

    def test_calc_distance_between_same_leaf(self):
        tested_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        first = tested_forest.roots[2].successors[1].successors[1]
        second = tested_forest.roots[2].successors[1].successors[1]
        result = tested_forest.calc_distance(first, second)
        proper_result = (0, 0)
        self.assertEqual(proper_result, result)

        new_first = second
        new_second = first
        new_result = tested_forest.calc_distance(new_first, new_second)
        new_proper_result = (-proper_result[0], -proper_result[1])
        self.assertEqual(new_proper_result, new_result)

    def test_calc_distance_between_same_leaf_root(self):
        tested_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        first = tested_forest.roots[1]
        second = tested_forest.roots[1]
        result = tested_forest.calc_distance(first, second)
        proper_result = (0, 0)
        self.assertEqual(proper_result, result)

        new_first = second
        new_second = first
        new_result = tested_forest.calc_distance(new_first, new_second)
        new_proper_result = (-proper_result[0], -proper_result[1])
        self.assertEqual(new_proper_result, new_result)

    def test_calc_distance_between_root_and_its_inner_successor(self):
        tested_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        first = tested_forest.roots[2]
        second = tested_forest.roots[2].successors[2]
        result = tested_forest.calc_distance(first, second)
        proper_result = (-1, -3)
        self.assertEqual(proper_result, result)

        new_first = second
        new_second = first
        new_result = tested_forest.calc_distance(new_first, new_second)
        new_proper_result = (-proper_result[0], -proper_result[1])
        self.assertEqual(new_proper_result, new_result)

    def test_calc_distance_between_root_and_its_leaf(self):
        tested_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        first = tested_forest.roots[2]
        second = tested_forest.roots[2].successors[2].successors[1]
        result = tested_forest.calc_distance(first, second)
        proper_result = (-2, -4)
        self.assertEqual(proper_result, result)

        new_first = second
        new_second = first
        new_result = tested_forest.calc_distance(new_first, new_second)
        new_proper_result = (-proper_result[0], -proper_result[1])
        self.assertEqual(new_proper_result, new_result)

    def test_calc_distance_between_roots(self):
        tested_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        first = tested_forest.roots[0]
        second = tested_forest.roots[2]
        result = tested_forest.calc_distance(first, second)
        proper_result = (0, -6)
        self.assertEqual(proper_result, result)

        new_first = second
        new_second = first
        new_result = tested_forest.calc_distance(new_first, new_second)
        new_proper_result = (-proper_result[0], -proper_result[1])
        self.assertEqual(new_proper_result, new_result)

    def test_calc_distance_between_root_and_other_roots_inner_node_from_left(self):
        tested_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        first = tested_forest.roots[2]
        second = tested_forest.roots[0].successors[1]
        result = tested_forest.calc_distance(first, second)
        proper_result = (-1, 5)
        self.assertEqual(proper_result, result)

        new_first = second
        new_second = first
        new_result = tested_forest.calc_distance(new_first, new_second)
        new_proper_result = (-proper_result[0], -proper_result[1])
        self.assertEqual(new_proper_result, new_result)

    def test_calc_distance_between_root_and_other_roots_inner_node_from_right(self):
        tested_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        first = tested_forest.roots[0]
        second = tested_forest.roots[2].successors[1]
        result = tested_forest.calc_distance(first, second)
        proper_result = (-1, -7)
        self.assertEqual(proper_result, result)

        new_first = second
        new_second = first
        new_result = tested_forest.calc_distance(new_first, new_second)
        new_proper_result = (-proper_result[0], -proper_result[1])
        self.assertEqual(new_proper_result, new_result)

    def test_calc_distance_between_root_and_other_roots_leaf_from_left(self):
        tested_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        first = tested_forest.roots[2]
        second = tested_forest.roots[0].successors[0]
        result = tested_forest.calc_distance(first, second)
        proper_result = (-1, 6)
        self.assertEqual(proper_result, result)

        new_first = second
        new_second = first
        new_result = tested_forest.calc_distance(new_first, new_second)
        new_proper_result = (-proper_result[0], -proper_result[1])
        self.assertEqual(new_proper_result, new_result)

    def test_calc_distance_between_root_and_other_roots_leaf_from_right(self):
        tested_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        first = tested_forest.roots[0]
        second = tested_forest.roots[2].successors[1].successors[0]
        result = tested_forest.calc_distance(first, second)
        proper_result = (-2, -7)
        self.assertEqual(proper_result, result)

        new_first = second
        new_second = first
        new_result = tested_forest.calc_distance(new_first, new_second)
        new_proper_result = (-proper_result[0], -proper_result[1])
        self.assertEqual(new_proper_result, new_result)

    def test_calc_distance_between_inner_node_and_other_roots_inner_node_from_left(self):
        tested_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        first = tested_forest.roots[2].successors[1]
        second = tested_forest.roots[0].successors[1]
        result = tested_forest.calc_distance(first, second)
        proper_result = (0, 6)
        self.assertEqual(proper_result, result)

        new_first = second
        new_second = first
        new_result = tested_forest.calc_distance(new_first, new_second)
        new_proper_result = (-proper_result[0], -proper_result[1])
        self.assertEqual(new_proper_result, new_result)

    def test_calc_distance_between_inner_node_and_other_roots_inner_node_from_right(self):
        tested_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        first = tested_forest.roots[0].successors[1]
        second = tested_forest.roots[2].successors[2]
        result = tested_forest.calc_distance(first, second)
        proper_result = (0, -8)
        self.assertEqual(proper_result, result)

        new_first = second
        new_second = first
        new_result = tested_forest.calc_distance(new_first, new_second)
        new_proper_result = (-proper_result[0], -proper_result[1])
        self.assertEqual(new_proper_result, new_result)

    def test_calc_distance_between_inner_node_and_other_roots_leaf_from_left(self):
        tested_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        first = tested_forest.roots[2].successors[1]
        second = tested_forest.roots[0].successors[1].successors[1]
        result = tested_forest.calc_distance(first, second)
        proper_result = (-1, 5)
        self.assertEqual(proper_result, result)

        new_first = second
        new_second = first
        new_result = tested_forest.calc_distance(new_first, new_second)
        new_proper_result = (-proper_result[0], -proper_result[1])
        self.assertEqual(new_proper_result, new_result)

    def test_calc_distance_between_inner_node_and_other_roots_leaf_from_right(self):
        tested_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [5], [3, 4, [5, 6, 7], [2, 5, 9]])
        first = tested_forest.roots[0].successors[1]
        second = tested_forest.roots[2].successors[2].successors[0]
        result = tested_forest.calc_distance(first, second)
        proper_result = (-1, -8)
        self.assertEqual(proper_result, result)

        new_first = second
        new_second = first
        new_result = tested_forest.calc_distance(new_first, new_second)
        new_proper_result = (-proper_result[0], -proper_result[1])
        self.assertEqual(new_proper_result, new_result)

    def test_calc_distance_between_adjacent_roots(self):
        tested_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [3, 4, [5, 6, 7], [2, 5, 9]])
        first = tested_forest.roots[0]
        second = tested_forest.roots[1]
        result = tested_forest.calc_distance(first, second)
        proper_result = (0, -5)
        self.assertEqual(proper_result, result)

        new_first = second
        new_second = first
        new_result = tested_forest.calc_distance(new_first, new_second)
        new_proper_result = (-proper_result[0], -proper_result[1])
        self.assertEqual(new_proper_result, new_result)

    def test_calc_distance_between_root_and_adjacent_roots_inner_node_from_left(self):
        tested_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [3, 4, [5, 6, 7], [2, 5, 9]])
        first = tested_forest.roots[1]
        second = tested_forest.roots[0].successors[1]
        result = tested_forest.calc_distance(first, second)
        proper_result = (-1, 4)
        self.assertEqual(proper_result, result)

        new_first = second
        new_second = first
        new_result = tested_forest.calc_distance(new_first, new_second)
        new_proper_result = (-proper_result[0], -proper_result[1])
        self.assertEqual(new_proper_result, new_result)

    def test_calc_distance_between_root_and_adjacent_roots_inner_node_from_right(self):
        tested_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [3, 4, [5, 6, 7], [2, 5, 9]])
        first = tested_forest.roots[0]
        second = tested_forest.roots[1].successors[1]
        result = tested_forest.calc_distance(first, second)
        proper_result = (-1, -6)
        self.assertEqual(proper_result, result)

        new_first = second
        new_second = first
        new_result = tested_forest.calc_distance(new_first, new_second)
        new_proper_result = (-proper_result[0], -proper_result[1])
        self.assertEqual(new_proper_result, new_result)

    def test_calc_distance_between_root_and_adjacent_roots_leaf_from_left(self):
        tested_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [3, 4, [5, 6, 7], [2, 5, 9]])
        first = tested_forest.roots[1]
        second = tested_forest.roots[0].successors[0]
        result = tested_forest.calc_distance(first, second)
        proper_result = (-1, 5)
        self.assertEqual(proper_result, result)

        new_first = second
        new_second = first
        new_result = tested_forest.calc_distance(new_first, new_second)
        new_proper_result = (-proper_result[0], -proper_result[1])
        self.assertEqual(new_proper_result, new_result)

    def test_calc_distance_between_root_and_adjacent_roots_leaf_from_right(self):
        tested_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [3, 4, [5, 6, 7], [2, 5, 9]])
        first = tested_forest.roots[0]
        second = tested_forest.roots[1].successors[1].successors[0]
        result = tested_forest.calc_distance(first, second)
        proper_result = (-2, -6)
        self.assertEqual(proper_result, result)

        new_first = second
        new_second = first
        new_result = tested_forest.calc_distance(new_first, new_second)
        new_proper_result = (-proper_result[0], -proper_result[1])
        self.assertEqual(new_proper_result, new_result)


    def test_calc_distance_between_inner_node_and_adjacent_roots_inner_node_from_left(self):
        tested_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [3, 4, [5, 6, 7], [2, 5, 9]])
        first = tested_forest.roots[1].successors[1]
        second = tested_forest.roots[0].successors[1]
        result = tested_forest.calc_distance(first, second)
        proper_result = (0, 5)
        self.assertEqual(proper_result, result)

        new_first = second
        new_second = first
        new_result = tested_forest.calc_distance(new_first, new_second)
        new_proper_result = (-proper_result[0], -proper_result[1])
        self.assertEqual(new_proper_result, new_result)

    def test_calc_distance_between_inner_node_and_adjacent_roots_inner_node_from_right(self):
        tested_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [3, 4, [5, 6, 7], [2, 5, 9]])
        first = tested_forest.roots[0].successors[1]
        second = tested_forest.roots[1].successors[2]
        result = tested_forest.calc_distance(first, second)
        proper_result = (0, -7)
        self.assertEqual(proper_result, result)

        new_first = second
        new_second = first
        new_result = tested_forest.calc_distance(new_first, new_second)
        new_proper_result = (-proper_result[0], -proper_result[1])
        self.assertEqual(new_proper_result, new_result)

    def test_calc_distance_between_inner_node_and_adjacent_roots_leaf_from_left(self):
        tested_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [3, 4, [5, 6, 7], [2, 5, 9]])
        first = tested_forest.roots[1].successors[1]
        second = tested_forest.roots[0].successors[1].successors[1]
        result = tested_forest.calc_distance(first, second)
        proper_result = (-1, 4)
        self.assertEqual(proper_result, result)

        new_first = second
        new_second = first
        new_result = tested_forest.calc_distance(new_first, new_second)
        new_proper_result = (-proper_result[0], -proper_result[1])
        self.assertEqual(new_proper_result, new_result)

    def test_calc_distance_between_inner_node_and_adjacent_roots_leaf_from_right(self):
        tested_forest = Forest.build_forest([2, 9, [8, 5, 7, 2], 8], [3, 4, [5, 6, 7], [2, 5, 9]])
        first = tested_forest.roots[0].successors[1]
        second = tested_forest.roots[1].successors[2].successors[0]
        result = tested_forest.calc_distance(first, second)
        proper_result = (-1, -7)
        self.assertEqual(proper_result, result)

        new_first = second
        new_second = first
        new_result = tested_forest.calc_distance(new_first, new_second)
        new_proper_result = (-proper_result[0], -proper_result[1])
        self.assertEqual(new_proper_result, new_result)

    def test_calc_distance_between_inner_nodes_in_deep_wide_forest(self):
        tested_forest = Forest.build_forest([0, [1, [2, [3, [4, 5, 6], 7, [8, 9, 0, 1]],
                                                        [2, 3, [4, 5, 6, 7], [8, 9]],
                                                        [0, 1, 2]],
                                                    [3, 4, [5, 6, 7, 8], 9]]],
                                            [0, 1, 2, 3], [4, [5, 6, 7], 8, [9, 0, 1]],
                                            [2, [3, [4, [5, 6, 7, 8], 9, 0],
                                                    [1, [2, 3, 4, 5], [6, 7, 8, 9], [0, 1, 2, 3]],
                                                    [4, [5, 6, 7, 8], [9, 0, 1, 2]]],
                                                [5, [6, 7, 8], [9, 0, 1], 2]])
        first = tested_forest.roots[0].successors[0].successors[0].successors[0].successors[2]
        second = tested_forest.roots[3].successors[1]
        result = tested_forest.calc_distance(first, second)
        proper_result = (3, -43)
        self.assertEqual(proper_result, result)

        new_first = second
        new_second = first
        new_result = tested_forest.calc_distance(new_first, new_second)
        new_proper_result = (-proper_result[0], -proper_result[1])
        self.assertEqual(new_proper_result, new_result)

    # TODO: Test tree-specific content and some forest functions on tree


if __name__ == '__main__':
    unittest.main()
