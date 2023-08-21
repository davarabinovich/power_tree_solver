
from threading import Thread
from PyQt6.QtWidgets import QMainWindow

from main_window import Ui_MainWindow
from electric_net import *
from solver import *


def config() -> [QMainWindow, Thread]:
    main_window = QMainWindow()
    main_ui = Ui_MainWindow()
    main_ui.setupUi(main_window)

    net = main_ui.graphview.electric_net
    solver = Solver(net)
    solution_thread = Thread(target=solver.work)

    return main_window, solution_thread
