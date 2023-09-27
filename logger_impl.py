
from os.path import dirname, basename
from logger_if import *


class LoggerImpl(LoggerIf):
    def __init__(self):
        super().__init__()
        self._is_actual_file = False
        self._file = None


    def set_log_location(self, path_to_net_file):
        directory = dirname(path_to_net_file)
        net_name = basename(path_to_net_file).removesuffix('.ens')
        log_file_full_path = directory + '/' + net_name
        self._file = log_file_full_path
        self._is_actual_file = True

    def write_action(self, action, *argv):
        if self._file is None:
            pass
        else:
            pass

    def remove_last_structure_record(self):
        if self._file is None:
            pass
        else:
            pass

    def mark_as_invalid(self):
        if self._file is None:
            pass
        else:
            pass

    def write_structure(self, structure):
        if self._file is None:
            pass
        else:
            pass
