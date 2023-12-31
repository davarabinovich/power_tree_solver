
class LoggerIf:
    def __init__(self):
        pass

    def create_log_file(self, path_to_net_file):
        raise NotImplementedError

    def log_loading(self, file_path):
        raise NotImplementedError

    def write_action(self, action, *argv):
        raise NotImplementedError

    def mark_as_invalid(self, validation_result: bool | str):
        raise NotImplementedError

    def write_generic_record(self, record):
        raise NotImplementedError

    @property
    def log_file(self):
        raise NotImplementedError
