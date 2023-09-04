
from PyQt6.QtCore import *
from electric_net import *


class FileSaver(QObject):
    def __init__(self, parent: QObject=None):
        super().__init__(parent)

    @pyqtSlot('PyQt_PyObject', str)
    def saveNetToFile(self, net: ElectricNet, net_file: str):
        self._file = open(net_file, 'w')
        self._net = net

        self._file.write('\n')
        inputs = self._net.get_inputs()
        for input in inputs:
            self._record_subtree(input)

        self._file.close()

    def _record_subtree(self, subroot: Forest.ForestNode, level=1):
        record = 'Level {level} {node}:\n{params}\n\n'.format(level=level, node=FileSaver._extract_node_type(subroot),
                                                              params=FileSaver._extract_node_params(subroot))
        self._file.write(record)
        sinks = self._net.get_sinks(subroot)
        for sink in sinks:
            self._record_subtree(sink, level+1)

    @staticmethod
    def _extract_node_type(node: Forest.ForestNode) -> str:
        type: ElectricNodeType = node.content.type
        if type == ElectricNodeType.INPUT:
            return 'Power Input'
        elif type == ElectricNodeType.CONVERTER:
            converter_type: ConverterType = node.content.converter_type
            if converter_type == ConverterType.LINEAR:
                return 'Linear Converter'
            else:
                return 'Switching Converter'
        else:
            consumer_type: ConverterType = node.content.consumer_type
            if consumer_type == ConsumerType.CONSTANT_CURRENT:
                return 'Constant Current Consumer'
            else:
                return 'Resistive Consumer'

    @staticmethod
    def _extract_node_params(node: Forest.ForestNode) -> str:
        node_data: ElectricNode = node.content
        params_str = '    Value: {value}{unit}'.format(value=node_data.value,
                                                       unit=FileSaver._extract_node_value_unit(node))
        if node_data.type != ElectricNodeType.LOAD:
            params_str += '\n    Load: {load}A'.format(load=node_data.load)

        return params_str

    @staticmethod
    def _extract_node_value_unit(node: Forest.ForestNode) -> str:
        node_data: ElectricNode = node.content
        if node_data.type != ElectricNodeType.LOAD:
            return 'V'
        else:
            consumer_type = node_data.consumer_type
            if consumer_type == ConsumerType.CONSTANT_CURRENT:
                return 'A'
            else:
                return 'Ohm'
