
import typing
import sys

from main_window import *
from solver import *
from net_view import *
from file_saver import *
from logger_impl import *


VERSION = (0, 1, "alfa")


class AppSupervisor(QObject):
    def __init__(self, main_window: QWidget, ui: Ui_MainWindow, solver: Solver, parent: QObject=None):
        super().__init__(parent)
        self._main_window = main_window
        self._ui = ui
        self._solver = solver
        self._active_net = None

        self._logger: LoggerImpl | None = None

    # TODO: Ensure, that it's not needed to resolve the net manually when saving is called
    # TODO: Program crushes, when cancel is pressed
    @pyqtSlot()
    def receiveSaveAsAction(self):
        file_url_tuple = QFileDialog.getSaveFileUrl(self._main_window,
                                                    caption="Save Electric Net", filter="Electric Net (*.ens)")
        if file_url_tuple[0].isEmpty():
            return False
        file_path = file_url_tuple[0].toString().removeprefix('file:///')

        if self._logger.log_file is None:
            self._logger.create_log_file(file_path)

        self.needToSaveActiveNet.emit(self._active_net, file_path)
        return True

    needToSaveActiveNet = pyqtSignal('PyQt_PyObject', str, name='needToSaveActiveNet')

    def handleChangingNet(self):
        pressed_button = QMessageBox.question(self._main_window,
                                              'The net was probably changed', 'Do you want to save changes in the net?')
        if pressed_button == QMessageBox.StandardButton.Yes:
            is_saved = self.receiveSaveAsAction()
            return is_saved
        return True

    @pyqtSlot()
    def receiveCreateNewAction(self):
        if self._active_net is not None:
            is_cancelled = not self.handleChangingNet()
            if is_cancelled:
                return
            self._ui.graphview.reset()

        self._ui.graphview.initNet()
        self._solver.setNet(self._ui.graphview.electric_net)
        self._active_net = self._ui.graphview.electric_net

        self._logger = LoggerImpl()
        self._ui.graphview.initView(self._logger)
        self._ui.graphview._addInput()

        self._ui.actionSaveAs.setEnabled(True)

    @pyqtSlot()
    def receiveLoadFromAction(self):
        if self._active_net is not None:
            is_cancelled = not self.handleChangingNet()
            if is_cancelled:
                return
            self._ui.graphview.reset()

        file_url_tuple = QFileDialog.getOpenFileUrl(self._main_window,
                                                    caption="Open Electric Net", filter="Electric Net (*.ens)")
        if file_url_tuple[0].toString() == '':
            return

        file_path = file_url_tuple[0].toString().removeprefix('file:///')
        file_loader = FileLoader()
        net = file_loader.load_net_from_file(file_path)
        self._solver.setNet(net)
        self._active_net = net

        self._logger = LoggerImpl(file_path)
        self._ui.graphview.initView(self._logger)
        self._ui.graphview.setNet(net)
        self._logger.log_loading(file_path)

        self._ui.actionSaveAs.setEnabled(True)


class MainWindow(QMainWindow):
    def __init__(self, ui: Ui_MainWindow):
        super().__init__()
        self._ui = ui
        self._ui.setupUi(self)
        self._supervisor: AppSupervisor | None = None
        self._was_first_resize = False

    # TODO: MainWindow shall know nothing about net
    def setSupervisor(self, sv: AppSupervisor):
        self._sv = sv

    def resizeEvent(self, a0: typing.Optional[QtGui.QResizeEvent]) -> None:
        if not self._was_first_resize:
            self._was_first_resize = True
            return

        old_size = a0.oldSize()
        new_size = a0.size()
        width_difference = new_size.width() - old_size.width()
        height_difference = new_size.height() - old_size.height()

        central_widget_geometry = self._ui.centralwidget.geometry()
        central_widget_geometry.setWidth(central_widget_geometry.width() + width_difference)
        central_widget_geometry.setHeight(central_widget_geometry.height() + height_difference)
        self._ui.centralwidget.setGeometry(central_widget_geometry)

        net_view_geometry = self._ui.graphview.geometry()
        net_view_geometry.setWidth(net_view_geometry.width() + width_difference)
        net_view_geometry.setHeight(net_view_geometry.height() + height_difference)
        self._ui.graphview.setGeometry(net_view_geometry)

    def closeEvent(self, a0: typing.Optional[QtGui.QCloseEvent]) -> None:
        if self._sv._active_net is None:
            a0.accept()
            return

        pressed_button = QMessageBox.question(self,
                                              'The net was probably changed', 'Do you want to save changes in the net?')
        if pressed_button == QMessageBox.StandardButton.Yes:
            is_saved = self._sv.receiveSaveAsAction()
            if is_saved:
                a0.accept()
            else:
                a0.ignore()
        else:
            a0.accept()

def main():
    app = QApplication(sys.argv)
    ui = Ui_MainWindow()
    window = MainWindow(ui)

    net_view = ui.graphview
    solver = Solver()
    net_view.contentChanged.connect(solver.recalculateChanges)
    solver.loadCalculated.connect(net_view.updateLoads)

    supervisor = AppSupervisor(window, ui, solver)
    window.setSupervisor(supervisor)
    file_saver = FileSaver()
    ui.actionSaveAs.triggered.connect(supervisor.receiveSaveAsAction)
    supervisor.needToSaveActiveNet.connect(file_saver.saveNetToFile)

    ui.actionCreateNew.triggered.connect(supervisor.receiveCreateNewAction)
    ui.actionLoadFrom.triggered.connect(supervisor.receiveLoadFromAction)

    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
