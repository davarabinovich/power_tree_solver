
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

    def create_input(self) -> ElectricNode:
        root = self._forest.create_root()
        input_data = ElectricNode()
        root.content = input_data
        return input_data
