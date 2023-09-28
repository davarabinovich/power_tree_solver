
class LoggerIf:
    def __init__(self):
        pass

    def set_log_file(self, path_to_net_file):
        raise NotImplementedError

    def write_action(self, action, *argv):
        raise NotImplementedError

    def remove_last_structure_record(self):
        raise NotImplementedError

    def mark_as_invalid(self):
        raise NotImplementedError

    def write_structure(self, structure):
        raise NotImplementedError

    def indent(self):
        raise NotImplementedError

    def is_log_file_set(self):
        raise NotImplementedError

    def save_log_file(self):
        raise NotImplementedError
