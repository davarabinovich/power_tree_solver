
import sys
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from app_config import *
from gui import *


VERSION = (0, 1, "alfa")


class AppSupervisor(QObject):
    def __init__(self, parent: QObject=None):
        super().__init__(parent)
        self._active_net = None

    def setActiveNet(self, net: ElectricNet):
        self._active_net = net

    @pyqtSlot()
    def receiveSaveAsAction(self):
        file_dialog = QFileDialog()
        file_dialog.show()
        self.needToSaveActiveNet.emit(self._active_net)

    needToSaveActiveNet = pyqtSignal('PyQt_PyObject', name='needToSaveActiveNet')


def main():
    app = QApplication(sys.argv)
    window = QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(window)

    net_view = ui.graphview
    net = net_view.electric_net
    solver = Solver(net)
    net_view.contentChanged.connect(solver.recalculateChanges)
    solver.loadCalculated.connect(net_view.updateLoads)

    supervisor = AppSupervisor()
    supervisor.setActiveNet(net)
    file_saver = FileSaver()
    ui.actionSaveAs.triggered.connect(supervisor.receiveSaveAsAction)
    supervisor.needToSaveActiveNet.connect(file_saver.saveNet)

    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
