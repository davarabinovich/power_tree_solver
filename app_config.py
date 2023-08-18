
from PyQt6.QtCore import *

import gui
import graph_gui

def configure (ui: common_gui.Ui_MainWindow):
    ui.graphview.rootAdded.connect()

@pyqtSlot()
def addRoot():
    pass
