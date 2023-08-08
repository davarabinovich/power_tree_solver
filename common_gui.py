
from PyQt6.QtWidgets import QMainWindow
from main_window import Ui_MainWindow
from graph_gui import *


# TODO: Implement singleton
class CommonGui:
    class ExtraGui(Exception): pass

    def __init__(self):
        if CommonGui._is_instance:
            raise CommonGui.ExtraGui
        self._is_instance = True

        self.window = QMainWindow()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self.window)

    def launch(self):
        self.window.show()

    _is_instance = False
