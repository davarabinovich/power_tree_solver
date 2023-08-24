
from threading import Thread
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *

from main_window import Ui_MainWindow
from electric_net import *
from solver import *
from file_saver import *

class TestIntern(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)

    @pyqtSlot()
    def slot(self):
        print("Captured internal")

    def __del__(self):
        print("Internal deleted")

def config(main_ui: Ui_MainWindow, test_extern):
    net_view = main_ui.graphview
    net = net_view.electric_net
    solver = Solver(net)
    net_view.contentChanged.connect(solver.recalculateChanges)
    solver.loadCalculated.connect(net_view.updateLoads)
    # test_intern = TestIntern()
    # main_ui.actionSaveAs.triggered.connect(test_intern.slot)
    main_ui.actionSaveAs.triggered.connect(test_extern.slot)
    # supervisor = AppSupervisor()
    # supervisor.setActiveNet(net)
    # file_saver = FileSaver()
    # main_ui.actionSaveAs.triggered.connect(supervisor.receiveSaveAsAction)
    # supervisor.needToSaveActiveNet.connect(file_saver.saveNet)

    solving_thread = Thread(target=solver.work)

    # return main_window, solving_thread

    # return test_intern



class AppSupervisor(QObject):
    def __init__(self, parent: QObject=None):
        super().__init__(parent)
        self._active_net = None

    def setActiveNet(self, net: ElectricNet):
        self._active_net = net

    @pyqtSlot()
    def receiveSaveAsAction(self):
        print("Captured")
        # self.needToSaveActiveNet.emit(self._active_net)

    needToSaveActiveNet = pyqtSignal('PyQt_PyObject', name='needToSaveActiveNet')
