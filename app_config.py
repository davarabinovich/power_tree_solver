
from threading import Thread
from PyQt6.QtWidgets import QMainWindow

from main_window import Ui_MainWindow
from electric_net import *
from solver import *


def config() -> [QMainWindow, Thread]:
    main_window = QMainWindow()
    main_ui = Ui_MainWindow()
    main_ui.setupUi(main_window)

    net_view = main_ui.graphview
    net = net_view.electric_net
    solver = Solver(net)
    net_view.contentChanged.connect(solver.recalculateChanges)
    solver.loadCalculated.connect(net_view.updateLoads)

    solving_thread = Thread(target=solver.work)

    return main_window, solving_thread
