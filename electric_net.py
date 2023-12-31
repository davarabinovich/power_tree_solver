
from enum import Enum
from tree import *


class ElectricNodeType(Enum):
    INPUT = 1
    CONVERTER = 2
    LOAD = 3

class ConverterType(Enum):
    LINEAR = 1
    SWITCHING = 2

class ConsumerType(Enum):
    CONSTANT_CURRENT = 1
    RESISTIVE = 2


class ElectricNode:
    class AccessToLoadLoad(Exception): pass
    class NotConverter(Exception): pass
    class NotConsumer(Exception): pass

    def __init__(self, node_type: ElectricNodeType):
        self._name = ''
        self._value = 0
        self._type = node_type
        self._load = 0

        if node_type == ElectricNodeType.CONVERTER:
            self._converter_type = ConverterType.SWITCHING
        if node_type == ElectricNodeType.LOAD:
            self._consumer_type = ConsumerType.CONSTANT_CURRENT

    @property
    def name(self):
        return self._name
    @name.setter
    def name(self, new_value):
        self._name = new_value

    @property
    def value(self):
        return self._value
    @value.setter
    def value(self, new_value):
        self._value = new_value

    @property
    def type(self):
        return self._type

    @property
    def converter_type(self):
        if self._type != ElectricNodeType.CONVERTER:
            raise ElectricNode.NotConverter
        return self._converter_type
    @converter_type.setter
    def converter_type(self, converter_type):
        if self._type != ElectricNodeType.CONVERTER:
            raise ElectricNode.NotConverter
        self._converter_type = converter_type

    @property
    def consumer_type(self):
        if self._type != ElectricNodeType.LOAD:
            raise ElectricNode.NotConsumer
        return self._consumer_type
    @consumer_type.setter
    def consumer_type(self, consumer_type):
        if self._type != ElectricNodeType.LOAD:
            raise ElectricNode.NotConsumer
        self._consumer_type = consumer_type

    @property
    def load(self):
        if self._type == ElectricNodeType.LOAD:
            raise ElectricNode.AccessToLoadLoad
        return self._load
    @load.setter
    def load(self, new_value):
        if self._type == ElectricNodeType.LOAD:
            raise ElectricNode.AccessToLoadLoad
        self._load = new_value


class ElectricNet:
    def __init__(self):
        self._forest = Forest()

    def create_input(self) -> Forest.ForestNode:
        root = self._forest.create_root()
        input_data = ElectricNode(ElectricNodeType.INPUT)
        root.content = input_data
        return root

    def add_converter(self, parent: Forest.ForestNode) -> Forest.ForestNode:
        node = self._forest.add_leaf(parent)
        converter_data = ElectricNode(ElectricNodeType.CONVERTER)
        converter_data.converter_type = ConverterType.SWITCHING
        node.content = converter_data
        return node

    def add_load(self, parent: Forest.ForestNode) -> Forest.ForestNode:
        leaf = self._forest.add_leaf(parent)
        load_data = ElectricNode(ElectricNodeType.LOAD)
        load_data.consumer_type = ConsumerType.CONSTANT_CURRENT
        leaf.content = load_data
        return leaf

    # TODO: This function assumes, that there is no free sinks; it needs to filter them
    def get_inputs(self) -> list[Forest.ForestNode]:
        inputs = []
        for root in self._forest.roots:
            inputs.append(root)
        return inputs

    @staticmethod
    def get_sinks(source_node: Forest.ForestNode) -> list[Forest.ForestNode]:
        sinks = []
        for successor in source_node.successors:
            sinks.append(successor)
        return sinks

    @property
    def forest(self):
        return self._forest
