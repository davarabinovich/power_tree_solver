
from net_view import *


EXTENSION = '.ens'


class FileSaver(QObject):
    def __init__(self, parent: QObject=None):
        super().__init__(parent)
        self._file = None
        self._net = None
        self._graph = None

    @pyqtSlot('PyQt_PyObject', str)
    def saveNetToFile(self, net_view: NetView, net_file: str):
        self._net = net_view.electric_net
        self._graph = net_view._graph_forest

        self._file = open(net_file, 'w')
        self._file.write('\n')

        last_hrids = net_view.get_actual_last_hrids()
        self._file.write('Last Power Input HRID: {hrid}\n'.format(hrid=last_hrids.power_inputs))
        self._file.write('Last Converter HRID: {hrid}\n'.format(hrid=last_hrids.converters))
        self._file.write('Last Consumer HRID: {hrid}\n'.format(hrid=last_hrids.consumers))
        self._file.write('\n\n\n')

        inputs = self._net.get_inputs()
        for index in range(len(inputs)):
            self._record_subtree(inputs[index], self._graph.roots[index])

        self._file.write('\n')
        self._file.close()

    def _record_subtree(self, electric_subroot: Forest.ForestNode, graphic_subroot: Forest.ForestNode, level=1):
        subroot_hrid = ''
        for item in graphic_subroot.content.childItems():
            if isinstance(item, QGraphicsProxyWidget):
                widget = item.widget()
                subroot_hrid = widget.hrid

        record = 'Level {level} {type} {hrid} {name}:\n{params}\n\n'\
            .format(level=level, type=FileSaver._extract_node_type(electric_subroot), hrid=subroot_hrid,
                    name=electric_subroot.content.name, params=FileSaver._extract_node_params(electric_subroot))

        self._file.write(record)
        sinks = ElectricNet.get_sinks(electric_subroot)
        for index in range(len(sinks)):
            self._record_subtree(sinks[index], graphic_subroot.successors[index], level+1)

    @staticmethod
    def _extract_node_type(node: Forest.ForestNode) -> str:
        node_type: ElectricNodeType = node.content.type
        if node_type == ElectricNodeType.INPUT:
            return 'Power_Input'
        elif node_type == ElectricNodeType.CONVERTER:
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
        self._file_content = []
        self._net: ElectricNet | None = None

    def load_net_from_file(self, path: str) -> tuple[ElectricNet, LastHrids] | None:
        self._file = open(path, 'r')
        raw_file_lines = self._file.read().splitlines()
        for line in raw_file_lines:
            if not len(line) == 0:
                self._file_content.append(line)

        try:
            self._net = ElectricNet()
            last_hrids = self._extract_last_hrids_from_file()
            self._build_net_by_file(self._file)
        except Exception as exception:
            return None

        self._file.close()
        return self._net, last_hrids

    def _extract_last_hrids_from_file(self) -> LastHrids:
        last_hrids = LastHrids(power_inputs=self._file_content[0].split()[-1],
                               converters=self._file_content[1].split()[-1],
                               consumers=self._file_content[2].split()[-1])
        return last_hrids

    def _build_net_by_file(self, file):
        cur_path: list[Forest.ForestNode] = []
        for line in self._file_content[3:]:
            # if len(line.split()) == 0:
            #     continue

            tokens = line.split()
            leading_token = tokens[0]
            if leading_token == 'Level':
                level = int(tokens[1])
                if level == 1:
                    node = self._net.create_input()
                    node.content.name = FileLoader._build_name_by_line_tokens(tokens)
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

    @staticmethod
    def _build_name_by_line_tokens(tokens: list[str]):
        if len(tokens) < 5:
            raise FileLoader.InvalidRecord

        name = ''
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
            node.content.name = FileLoader._build_name_by_line_tokens(tokens)
            return node
        elif type_token == 'Linear_Converter':
            node = self._net.add_converter(parent)
            node.content.converter_type = ConverterType.LINEAR
            node.content.name = FileLoader._build_name_by_line_tokens(tokens)
            return node
        elif type_token == 'Constant_Current_Consumer':
            node = self._net.add_load(parent)
            node.content.consumer_type = ConsumerType.CONSTANT_CURRENT
            node.content.name = FileLoader._build_name_by_line_tokens(tokens)
            return node
        elif type_token == 'Resistive_Consumer':
            node = self._net.add_load(parent)
            node.content.consumer_type = ConsumerType.RESISTIVE
            node.content.name = FileLoader._build_name_by_line_tokens(tokens)
            return node
        else:
            raise FileLoader.InvalidRecord
