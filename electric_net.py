
from tree import *


class ElectricNode:
    def __init__(self):
        self._value = 0

    @property
    def value(self):
        return self._value
    @value.setter
    def value(self, new_value):
        self._value = new_value


class ElectricNet:
    def __init__(self):
        self._forest = Forest()

    def create_input(self) -> Forest.ForestNode:
        root = self._forest.create_root()
        input_data = ElectricNode()
        root.content = input_data
        return root

    def add_converter(self, parent: Forest.ForestNode) -> Forest.ForestNode:
        node = self._forest.add_leaf(parent)
        converter_data = ElectricNode()
        node.content = converter_data
        return node

    def add_load(self, parent: Forest.ForestNode) -> Forest.ForestNode:
        leaf = self._forest.add_leaf(parent)
        load_data = ElectricNode()
        leaf.content = load_data
        return leaf

    # TODO: This function assumes, that there is no free sinks
    def getInputs(self) -> list[ElectricNode]:
        inputs = []
        for root in self._forest.roots:
            inputs.append(root.content)
        return inputs
