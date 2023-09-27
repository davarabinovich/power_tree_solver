
class LoggerIf:
    def __init__(self):
        pass

    def set_log_location(self, path_to_net_file):
        raise NotImplementedError

    def write_action(self, action, *argv):
        raise NotImplementedError

    def remove_last_structure_record(self):
        raise NotImplementedError

    def mark_as_invalid(self):
        raise NotImplementedError

    def write_structure(self, structure):
        raise NotImplementedError
