
from os.path import dirname, basename
from logger_if import *
from net_view import *


class LoggerImpl(LoggerIf):
    # Public interface
    def __init__(self, path_to_net_file=None):
        super().__init__()
        self._is_actual_file = False
        self._file = None
        self._temp_log = '\n'
        if path_to_net_file is not None:
            self._activate_file(path_to_net_file)

    def set_log_file(self, path_to_net_file):
        self._activate_file(path_to_net_file)
        self._dump_temp_log_to_file()

    def write_action(self, action, *argv):
        if self._file is None:
            self._write_action_to_temp_log(action, argv)
        else:
            self._write_action_to_file(action, argv)

    def remove_last_structure_record(self):
        if self._file is None:
            self._remove_last_structure_record_from_temp_log()
        else:
            self._remove_last_structure_record_from_file()

    def mark_as_invalid(self):
        if self._file is None:
            self._mark_as_invalid_in_temp_log()
        else:
            self._mark_as_invalid_in_file()

    def write_structure(self, structure):
        if self._file is None:
            self._write_structure_to_temp_log(structure)
        else:
            self._write_action_to_file(structure)

    def indent(self):
        if self._file is None:
            self._indent_in_temp_log()
        else:
            self._indent_in_file()

    def is_log_file_set(self):
        result = self._file is not None
        return result

    def save_log_file(self):
        raise NotImplementedError


    # Private part
    def _activate_file(self, path_to_net_file):
        directory = dirname(path_to_net_file)
        net_name = basename(path_to_net_file).removesuffix('.ens')
        log_file_full_path = directory + '/' + net_name
        self._file = log_file_full_path
        self._is_actual_file = True

    def _dump_temp_log_to_file(self):
        pass

    def _write_action_to_temp_log(self, action, *argv):
        self._temp_log += '{action}, Name: {name}'.format(action=action, name=argv[0])

        # TODO: There is knowledge about NetVview, but it doesn't reflect in code. It need to create explicit dependency
        if action in ['Place Converter', 'Add Converter', 'Place Consumer', 'Place Consumer']:
            self._temp_log += ', Parent: {parent_name}'.format(parent_name=argv[1])
        elif action == 'Delete Ancestor Reconnecting':
            self._temp_log += ', New Parent: {parent_name}'.format(parent_name=argv[1])

        self._temp_log += '\n\n'

    def _remove_last_structure_record_from_temp_log(self):
        pass

    def _mark_as_invalid_in_temp_log(self):
        pass

    def _write_structure_to_temp_log(self, structure: NetView):
        electric_forest = structure.electric_net._forest
        graphic_forest = structure._forest
        scene = structure.scene().items()

        self._temp_log += 'Forest of Electric Net: \n{forest_string_view}\n\n'\
            .format(forest_string_view=electric_forest.generate_string_view())
        self._temp_log += 'Forest of Graph View: \n{forest_string_view}\n\n' \
            .format(forest_string_view=graphic_forest.generate_string_view())

        self._write_scene_to_temp_log(scene)

    def _indent_in_temp_log(self):
        pass

    def _write_action_to_file(self, action, *argv):
        pass

    def _remove_last_structure_record_from_file(self):
        pass

    def _mark_as_invalid_in_file(self):
        pass

    def _write_structure_to_file(self, structure):
        pass

    def _indent_in_file(self):
        pass

    def _write_scene_to_temp_log(self, scene: list[QGraphicsItem]):
        pass

    def _write_scene_to_file(self, scene: list[QGraphicsItem]):
        pass
