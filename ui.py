
from PyQt6.QtWidgets import QMainWindow
from main_window import Ui_MainWindow
from drawing import *


# TODO: Implement singleton
class Ui:
    class ExtraUi(Exception): pass

    def __init__(self):
        if Ui._is_instance:
            raise Ui.ExtraUi
        self._is_instance = True

        self.window = QMainWindow()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self.window)

        self.drawing_area = DrawingArea()
        self.ui.graphicsView.setScene(self.drawing_area.scene)

    def launch(self):
        self.window.show()

    _is_instance = False
