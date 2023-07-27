
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
        if self.expected.parent != other.parent:
            return False
        if self.expected.content != other.content:
            return False

        for index in range(len(self.expected.successors)):
            successor_matcher = NodeFullTreeMatcher(self.expected.successors[index])
            if not successor_matcher.__eq__(other.successors[index]):
                return False

        return True


class TestNodeDisconnect(unittest.TestCase):
    def test_disconnect_leaf_from_none(self):
        node = build_tree([3])
        comparing_node = build_tree([3])
        is_exception = False
        try:
            node.disconnect()
        except:
            is_exception = True
        self.assertFalse(is_exception)
        self.assertEqual(NodeFullTreeMatcher(comparing_node), node)

    def test_disconnect_subtree_from_none(self):
        subroot = build_tree([3, 4, [9, 7, 5]])
        # comparing_subroot = build_tree([3, 4, [9, 7, 5]])
        # is_exception = False
        # try:
        #     subroot.disconnect()
        # except:
        #     is_exception = True
        # self.assertFalse(is_exception)
        # self.assertEqual(NodeFullTreeMatcher(comparing_subroot), subroot)

        # root = build_tree([1, [2, 9, [8, 5, 7, 2], 8], 5 , [3, 4, [5, 6, 7], [2, 5, 9]], 7])
        # node = root.successors[0].successors[0]
        # TODO: Test disconnection from None, from root, from inner node, leaf and subtree

    def test_connect_to(self):
        pass
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
