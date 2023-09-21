
from PyQt6.QtCore import *
from electric_net import *


class FileSaver(QObject):
    def __init__(self, parent: QObject=None):
        super().__init__(parent)
        self._file = None
        self._net = None

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
        record = 'Level {level} {type} {name}:\n{params}\n\n'.format(level=level,
                                                                     type=FileSaver._extract_node_type(subroot),
                                                                     name=subroot.content.name,
                                                                     params=FileSaver._extract_node_params(subroot))
        self._file.write(record)
        sinks = self._net.get_sinks(subroot)
        for sink in sinks:
            self._record_subtree(sink, level+1)

    @staticmethod
    def _extract_node_type(node: Forest.ForestNode) -> str:
        type: ElectricNodeType = node.content.type
        if type == ElectricNodeType.INPUT:
            return 'Power_Input'
        elif type == ElectricNodeType.CONVERTER:
            converter_type: ConverterType = node.content.converter_type
            if converter_type == ConverterType.LINEAR:
                return 'Linear_Converter'
            else:
                return 'Switching_Converter'
        else:
            consumer_type: ConverterType = node.content.consumer_type
            if consumer_type == ConsumerType.CONSTANT_CURRENT:
                return 'Constant_Current_Consumer'
            else:
                return 'Resistive_Consumer'

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


class FileLoader(QObject):
    class IncorrectNodeLevel(Exception): pass
    class InvalidRecord(Exception): pass

    def __init__(self, parent: QObject=None):
        super().__init__(parent)
        self._file = None
        self._net: ElectricNet|None = None

    def load_net_from_file(self, path: str):
        self._file = open(path, 'r')
        self._net = ElectricNet()
        self._build_net_by_file(self._file)
        return self._net

    def _build_net_by_file(self, file):
        cur_path: list[Forest.ForestNode] = []
        file_lines = file.read().splitlines()
        for line in file_lines:
            if len(line.split()) == 0:
                continue

            tokens = line.split()
            leading_token = tokens[0]
            if leading_token == 'Level':
                level = int(tokens[1])
                if level == 1:
                    node = self._net.create_input()
                    node.content.name = self._build_name_by_line_tokens(tokens)
                    cur_path = [node]
                elif level < len(cur_path):
                    cur_path = cur_path[:level]
                    parent = cur_path[-2]
                    node = self._build_node_by_record(parent, tokens)
                    cur_path[-1] = node
                elif level == len(cur_path):
                    parent = cur_path[-2]
                    node = self._build_node_by_record(parent, tokens)
                    cur_path[-1] = node
                elif level == len(cur_path)+1:
                    parent = cur_path[-1]
                    node = self._build_node_by_record(parent, tokens)
                    cur_path.append(node)
                else:
                    raise FileLoader.IncorrectNodeLevel
            elif leading_token == 'Value:':
                if cur_path[-1].content.type == ElectricNodeType.LOAD:
                    if cur_path[-1].content.consumer_type == ConsumerType.RESISTIVE:
                        value = tokens[1][:-3]
                    else:
                        value = tokens[1][:-1]
                else:
                    value = tokens[1][:-1]
                cur_path[-1].content.value = float(value)
            elif leading_token == 'Load:':
                if cur_path[-1].content.type == ElectricNodeType.LOAD:
                    raise FileLoader.InvalidRecord
                load = tokens[1][:-1]
                cur_path[-1].content.load = float(load)

    def _build_name_by_line_tokens(self, tokens: list[str]):
        if len(tokens) == 4 and tokens[2] == ':':
            return ''

        name = tokens[3]
        for token in tokens[4:]:
            name += ' ' + token
        name = name[:-1]
        return name

    def _build_node_by_record(self, parent: Forest.ForestNode, tokens: list[str]) -> Forest.ForestNode:
        type_token = tokens[2]
        if type_token == 'Power_input':
            raise FileLoader.IncorrectNodeLevel

        elif type_token == 'Switching_Converter':
            node = self._net.add_converter(parent)
            node.content.converter_type = ConverterType.SWITCHING
            node.content.name = self._build_name_by_line_tokens(tokens)
            return node
        elif type_token == 'Linear_Converter':
            node = self._net.add_converter(parent)
            node.content.converter_type = ConverterType.LINEAR
            node.content.name = self._build_name_by_line_tokens(tokens)
            return node
        elif type_token == 'Constant_Current_Consumer':
            node = self._net.add_load(parent)
            node.content.consumer_type = ConsumerType.CONSTANT_CURRENT
            node.content.name = self._build_name_by_line_tokens(tokens)
            return node
        elif type_token == 'Resistive_Consumer':
            node = self._net.add_load(parent)
            node.content.consumer_type = ConsumerType.RESISTIVE
            node.content.name = self._build_name_by_line_tokens(tokens)
            return node
        else:
            raise FileLoader.InvalidRecord
