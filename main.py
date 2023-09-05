
import sys
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from app_config import *
from gui import *
from net_view import *


VERSION = (0, 1, "alfa")


class AppSupervisor(QObject):
    def __init__(self, main_window: QWidget, ui: Ui_MainWindow, solver: Solver, parent: QObject=None):
        super().__init__(parent)
        self._main_window = main_window
        self._ui = ui
        self._solver = solver
        self._active_net = None

    # TODO: Ensure, that it's not needed to resolve the net manually when saving is called
    # TODO: Program crushes, when cancel is pressed
    @pyqtSlot()
    def receiveSaveAsAction(self):
        file_url_tuple = QFileDialog.getSaveFileUrl(self._main_window,
                                                          caption="Save Electric Net", filter="Electric Net (*.ens)")
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

    @pyqtSlot()
    def receiveCreateNewAction(self):
        self._ui.graphview.initNet()
        self._solver.setNet(self._ui.graphview.electric_net)
        self._active_net = self._ui.graphview.electric_net
        self._ui.graphview.initView()
        self._ui.graphview._addInput()

        self._ui.actionCreateNew.setDisabled(True)
        self._ui.actionSaveAs.setEnabled(True)

    @pyqtSlot()
    def receiveLoadFromAction(self):
        if self._active_net is not None:
            self.receiveQuit()

        file_url_tuple = QFileDialog.getOpenFileUrl(self._main_window,
                                                    caption="Open Electric Net", filter="Electric Net (*.ens)")
        file_path = file_url_tuple[0].toString().removeprefix('file:///')
        file_loader = FileLoader()
        net = file_loader.load_net_from_file(file_path)
        self._solver.setNet(net)
        self._active_net = net
        self._ui.graphview.setNet(net)

        self._ui.actionCreateNew.setDisabled(True)
        self._ui.actionSaveAs.setEnabled(True)


def main():
    app = QApplication(sys.argv)
    window = QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(window)

    net_view = ui.graphview
    solver = Solver()
    net_view.contentChanged.connect(solver.recalculateChanges)
    solver.loadCalculated.connect(net_view.updateLoads)

    supervisor = AppSupervisor(window, ui, solver)
    file_saver = FileSaver()
    ui.actionSaveAs.triggered.connect(supervisor.receiveSaveAsAction)
    supervisor.needToSaveActiveNet.connect(file_saver.saveNetToFile)

    app.aboutToQuit.connect(supervisor.receiveQuit)

    ui.actionCreateNew.triggered.connect(supervisor.receiveCreateNewAction)
    ui.actionLoadFrom.triggered.connect(supervisor.receiveLoadFromAction)

    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
