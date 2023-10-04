
from typing import Optional
from numpy import isclose
from PyQt6.QtCore import *
from settings import *
from electric_net import *


class Solver(QObject):
    class LoadCalculationForLoad(Exception): pass
    class ConsumptionCalculationForInput(Exception): pass

    def __init__(self, parent: QObject=None):
        super().__init__(parent)
        self._electric_net = None

    def set_net(self, net: ElectricNet):
        self._electric_net = net

    def solve(self):
        power_inputs = self._electric_net.get_inputs()
        for power_input in power_inputs:
            self.calc_and_write_load(power_input)

    def calc_and_write_load(self, source: Forest.ForestNode) -> Optional[float]:
        source_data: ElectricNode = source.content
        if source_data.type == ElectricNodeType.LOAD:
            raise Solver.LoadCalculationForLoad

        if type(source_data.value) is not float or isclose(source_data.value, 0.0, EPSILON):
            return None

        load = 0
        sinks = ElectricNet.get_sinks(source)
        for sink in sinks:
            sink_data: ElectricNode = sink.content
            if sink_data.type == ElectricNodeType.CONVERTER:
                converter_load = self.calc_and_write_load(sink)
                if type(converter_load) is float:
                    converter_consumption = Solver.calc_consumption(sink)
                    load += converter_consumption
                else:
                    return None
            else:
                load_value = sink_data.value
                if type(load_value) is not float:
                    return None
                else:
                    if sink_data.consumer_type == ConsumerType.CONSTANT_CURRENT:
                        load += sink_data.value
                    else:
                        current = source_data.value / sink_data.value
                        load += current

        source_data.load = load
        return load

    @staticmethod
    def calc_consumption(sink: Forest.ForestNode):
        sink_data: ElectricNode = sink.content
        if sink_data.type == ElectricNodeType.INPUT:
            raise Solver.ConsumptionCalculationForInput

        if sink_data.type == ElectricNodeType.CONVERTER:
            if sink_data.converter_type == ConverterType.LINEAR:
                return sink_data.load
            else:
                sink_parent: Forest.ForestNode = sink.parent
                parent_value = sink_parent.content.value
                consumption = (sink_data.value / parent_value) * sink_data.load
                return consumption
        else:
            return sink_data.value

    loadCalculated = pyqtSignal(name='loadCalculated')

    @pyqtSlot()
    def recalculateChanges(self):
        self.solve()
        self.loadCalculated.emit()
