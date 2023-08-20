
from PyQt6.QtWidgets import QMainWindow

from main_window import Ui_MainWindow
from electric_net import *


def config() -> QMainWindow:
    # net = ElectricNet()
    main_window = QMainWindow()
    main_ui = Ui_MainWindow()
    main_ui.setupUi(main_window)
    # main_ui.graphview.setElectricNet(net)

    return main_window
