
from os.path import dirname, basename
from datetime import datetime
from net_view import *


class LoggerImpl(LoggerIf):
    # Public interface
    class NoLogFile(Exception): pass
    class AttemptToInvalidateGoodView(Exception): pass
    class BadValidationResult(Exception): pass

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
        action_record = LoggerImpl._build_action_record(action, *argv)
        self._write_new_record(action_record)

    def log_loading(self, file_path):
        file = open(file_path, 'r')
        file_content = file.read()
        file.close()

        if self._log_file is None:
            raise LoggerImpl.NoLogFile

        file_content += '\n\n'
        self._write_new_record(file_content)

    def mark_as_invalid(self, validation_result: bool | str):
        invalidate_record = LoggerImpl._build_mark_as_invalid_record(validation_result)
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
        file.write('\n\n\n\nSession from {date_and_time}\n\n'.format(date_and_time=datetime.now()))
        file.close()

    def _dump_temp_log_to_file(self):
        file = open(self._log_file, 'a')
        file.write(self._temp_log)
        file.close()

    @staticmethod
    def _build_action_record(action, *argv):
        new_record = '{action}, Name: {name}'.format(action=action, name=argv[0])

        # TODO: There is knowledge about NetView, but it doesn't reflect in code. It needs to create explicit dependency
        if action in ['Place Converter', 'Add Converter', 'Place Consumer', 'Add Consumer']:
            new_record += ', Parent: {parent_name}'.format(parent_name=argv[1])
        elif action == 'Delete Ancestor Reconnecting':
            new_record += ', New Parent: {parent_name}'.format(parent_name=argv[1])

        new_record += '\n\n'
        return new_record

    @staticmethod
    def _build_mark_as_invalid_record(validation_result: bool | str):
        new_record = 'Has considered as invalid '
        if type(validation_result) == bool:
            if validation_result:
                raise LoggerImpl.AttemptToInvalidateGoodView
            else:
                cause_formulation = 'because validation fails.'
        elif type(validation_result) == str:
            cause_formulation = 'due to exception during validation: ' + validation_result
        else:
            raise LoggerImpl.BadValidationResult
        new_record += cause_formulation

        new_record += '\n\n'
        return new_record

    def _write_new_record(self, record):
        if self._log_file is None:
            self._temp_log += record
        else:
            file = open(self._log_file, 'a')
            file.write(record)
            file.close()
