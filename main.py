
import sys
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from app_config import *
from gui import *


VERSION = (0, 1, "alfa")


class AppSupervisor(QObject):
    def __init__(self, main_window: QWidget, parent: QObject=None):
        super().__init__(parent)
        self._main_window = main_window
        self._active_net = None

    def setActiveNet(self, net: ElectricNet):
        self._active_net = net

    # TODO: Ensure, that it's not needed to resolve the net manually when saving is called
    # TODO: Program crushes, when cancel is pressed
    @pyqtSlot()
    def receiveSaveAsAction(self):
        file_url_tuple = QFileDialog.getSaveFileUrl(self._main_window,
                                                          caption="Save Electric Net", filter="Electric Net (*.ens)")
        if file_url_tuple[0].isEmpty():
            return
        file_path = file_url_tuple[0].toString().removeprefix('file:///')
        self.needToSaveActiveNet.emit(self._active_net, file_path)

    needToSaveActiveNet = pyqtSignal('PyQt_PyObject', str, name='needToSaveActiveNet')

    @pyqtSlot()
    # TODO: It shall be called in only case, when some changes was performed from the last saving.
    # TODO: Main Window disappear, when messageBox pops up
    def receiveQuit(self):
        button = QMessageBox.question(self._main_window,
                                      'The net was probably changed', 'Do you want to save changes in the net?')
        if button == QMessageBox.StandardButton.Yes:
            self.receiveSaveAsAction()


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

    supervisor = AppSupervisor(window)
    supervisor.setActiveNet(net)
    file_saver = FileSaver()
    ui.actionSaveAs.triggered.connect(supervisor.receiveSaveAsAction)
    supervisor.needToSaveActiveNet.connect(file_saver.saveNetToFile)

    app.aboutToQuit.connect(supervisor.receiveQuit)

    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
