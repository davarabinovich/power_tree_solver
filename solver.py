
from electric_net import *


class Solver:
    def __init__(self, electric_net: ElectricNet):
        self._electric_net = electric_net

    def work(self):
        while(True):
            self.solve()

    def is_completed(self):
        return False

    def solve(self):
        inputs = self._electric_net.getInputs()
        for input in inputs:
            self.calcConsumption(input)

    def calcConsumption(self, ElectricNode):
        print(1)
