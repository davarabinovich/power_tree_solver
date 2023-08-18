
from PyQt6.QtWidgets import QMainWindow
from main_window import Ui_MainWindow


# TODO: Implement singleton
class Gui:
    class ExtraGui(Exception): pass

    def __init__(self):
        if Gui._is_instance:
            raise Gui.ExtraGui
        Gui._is_instance = True

        self._window = QMainWindow()
        self._ui = Ui_MainWindow()
        self._ui.setupUi(self._window)

    def launch(self):
        self._window.show()

    _is_instance = False
