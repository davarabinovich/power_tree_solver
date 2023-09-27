
from PyQt6.QtWidgets import QMainWindow


# TODO: Implement singleton
class Gui:
    class ExtraGui(Exception): pass

    def __init__(self, main_window: QMainWindow):
        if Gui._is_instance:
            raise Gui.ExtraGui
        Gui._is_instance = True
        self._window = main_window

    def launch(self):
        self._window.show()

    _is_instance = False
