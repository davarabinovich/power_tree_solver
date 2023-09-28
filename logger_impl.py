
from os.path import dirname, basename
from datetime import datetime
from net_view import *


class LoggerImpl(LoggerIf):
    # Public interface
    def __init__(self, file=None):
        super().__init__()
        self._log_file = None
        self._temp_log = '\n'
        if file is not None:
            self._activate_file(file)

    def create_log_file(self, path_to_net_file):
        self._activate_file(path_to_net_file)
        self._dump_temp_log_to_file()

    def write_action(self, action, *argv):
        action_record = self._build_action_record(action. argv)
        self._write_new_record(action_record)

    def mark_as_invalid(self):
        invalidate_record = self._build_mark_as_invalid_record()
        self._write_new_record(invalidate_record)

    @property
    def log_file(self):
        return self._log_file


    # Private part
    def _activate_file(self, path_to_net_file):
        directory = dirname(path_to_net_file)
        net_name = basename(path_to_net_file).removesuffix('.ens')
        log_file_full_path = directory + '/' + net_name
        self._log_file = log_file_full_path

        file = open(self._log_file, 'a')
        file.write('\n\n\n\nSession form {date_and_time}\n\n'.format(date_and_time=datetime.now()))
        file.close()

    def _dump_temp_log_to_file(self):
        file = open(self._log_file, 'a')
        file.write(self._temp_log)
        file.close()

    def _build_action_record(self, action, *argv):
        new_record = '{action}, Name: {name}'.format(action=action, name=argv[0])

        # TODO: There is knowledge about NetView, but it doesn't reflect in code. It need to create explicit dependency
        if action in ['Place Converter', 'Add Converter', 'Place Consumer', 'Place Consumer']:
            new_record += ', Parent: {parent_name}'.format(parent_name=argv[1])
        elif action == 'Delete Ancestor Reconnecting':
            new_record += ', New Parent: {parent_name}'.format(parent_name=argv[1])

        new_record += '\n\n'
        return new_record

    def _build_mark_as_invalid_record(self):
        new_record = 'Has become invalid'
        new_record += '\n\n'
        return new_record

    def _write_new_record(self, record):
        if self._log_file is None:
            self._temp_log += record
        else:
            file = open(self._log_file, 'a')
            file.write(record)
            file.close()
