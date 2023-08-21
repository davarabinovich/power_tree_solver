
from typing import Optional
from PyQt6.QtCore import *
from electric_net import *


class Solver:
    class LoadCalculationForLoad(Exception): pass
    class ConsumptionCalculationForInput(Exception): pass

    def __init__(self, electric_net: ElectricNet):
        self._electric_net = electric_net

    def work(self):
        while(True):
            self.solve()

    def is_completed(self):
        return False

    def solve(self):
        power_inputs = self._electric_net.get_inputs()
        for power_input in power_inputs:
            self.calc_and_write_load(power_input)

    def calc_and_write_load(self, source: Forest.ForestNode) -> Optional[float]:
        source_data: ElectricNode = source.content
        if source_data.type == ElectricNodeType.LOAD:
            raise Solver.LoadCalculationForLoad

        if type(source_data.value) is not float:
            return None

        consumption = 0
        sinks = self._electric_net.get_sinks(source)
        for sink in sinks:
            sink_data: ElectricNode = sink.content
            if sink_data.type == ElectricNodeType.CONVERTER:
                converter_load = self.calc_and_write_load(sink)
                if type(converter_load) is float:
                    converter_consumption = self.calc_consumption(sink)
                    consumption += converter_consumption
                else:
                    return None
            else:
                load_value = sink_data.value
                if type(load_value) is float:
                    consumption += sink_data.value
                else:
                    return None

        source_data.consumption = consumption
        return consumption

    def calc_consumption(self, sink: Forest.ForestNode):
        sink_data: ElectricNode = sink.content
        if sink_data.type == ElectricNodeType.INPUT:
            raise Solver.ConsumptionCalculationForInput

        if sink_data.type == ElectricNodeType.CONVERTER:
            sink_parent: Forest.ForestNode = sink.parent
            parent_value = sink_parent.content.value
            consumption = (parent_value / sink_data.value) * sink_data.load
            return consumption
        else:
            return sink_data.value

    loadCalculated = pyqtSignal(name='loadCalculated')

    @pyqtSlot()
    def recalculateChanges(self):
        self.solve()
        self.loadCalculated.emit()
