
import sys

from main_window import *
from solver import *
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
    @pyqtSlot()
    def receiveSaveAsAction(self):
        file_url_tuple = QFileDialog.getSaveFileUrl(self._main_window,
                                                    caption='Save Electric Net',
                                                    filter='Electric Net (*{extension})'.format(extension=EXTENSION))
        if file_url_tuple[0].isEmpty():
            return False
        file_path: str = file_url_tuple[0].toString().removeprefix('file:///')
        if not file_path.endswith(EXTENSION):
            file_path += EXTENSION

        if self._logger.log_file is None:
            self._logger.create_log_file(file_path)

        self.needToSaveActiveNet.emit(self._ui.graphview, file_path)
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

        self._ui.graphview.init_net()
        self._solver.set_net(self._ui.graphview.electric_net)
        self._active_net = self._ui.graphview.electric_net

        self._logger = LoggerImpl()
        self._ui.graphview.init_view(self._logger)
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

        reading_result = file_loader.load_net_from_file(file_path)
        if reading_result is None:
            message_box_title = 'Bad .ens file'
            message_box_text = 'The pts application cannot parse the file you have specified'
            QMessageBox.critical(self._main_window, message_box_title, message_box_text)
            return

        net, first_hrids = reading_result
        self._solver.set_net(net)
        self._active_net = net

        self._logger = LoggerImpl(file_path)
        self._ui.graphview.init_view(self._logger)
        self._ui.graphview.set_net(net, first_hrids)
        self._logger.log_loading(file_path)

        self._ui.actionSaveAs.setEnabled(True)


class MainWindow(QMainWindow):
    def __init__(self, ui: Ui_MainWindow):
        super().__init__()
        self._ui = ui
        self._ui.setupUi(self)
        self._supervisor: AppSupervisor | None = None
        self._was_first_resize = False
        self._sv: AppSupervisor | None = None

        self._ui.graphview.validityStatusChanged.connect(self.markValidity)

        # TODO: MainWindow shall know nothing about net
    def set_supervisor(self, sv: AppSupervisor):
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

        file_saving_message_box = QMessageBox(QMessageBox.Icon.Warning, 'The net was probably changed',
                                              'Do you want to save changes in the net?', parent=self)
        save_button = file_saving_message_box.addButton('Yes', QMessageBox.ButtonRole.YesRole)
        not_save_button = file_saving_message_box.addButton('No', QMessageBox.ButtonRole.DestructiveRole)
        close_button = file_saving_message_box.addButton('', QMessageBox.ButtonRole.RejectRole)
        close_button.hide()
        file_saving_message_box.exec()

        pressed_button = file_saving_message_box.clickedButton()
        if pressed_button == save_button:
            is_saved = self._sv.receiveSaveAsAction()
            if is_saved:
                a0.accept()
            else:
                a0.ignore()
        elif pressed_button == not_save_button:
            a0.accept()
        else:
            a0.ignore()

    @pyqtSlot(bool)
    def markValidity(self, is_valid):
        if is_valid:
            rgb_code = '0, 180, 33'
        else:
            rgb_code = '255, 0, 0'
        style_sheet = 'background-color: rgb({code});'.format(code=rgb_code)
        self._ui.statusBar.setStyleSheet(style_sheet)

def main():
    app = QApplication(sys.argv)
    ui = Ui_MainWindow()
    window = MainWindow(ui)

    net_view = ui.graphview
    solver = Solver()
    net_view.contentChanged.connect(solver.recalculateChanges)
    solver.loadCalculated.connect(net_view.updateLoads)

    supervisor = AppSupervisor(window, ui, solver)
    window.set_supervisor(supervisor)
    file_saver = FileSaver()
    ui.actionSaveAs.triggered.connect(supervisor.receiveSaveAsAction)
    supervisor.needToSaveActiveNet.connect(file_saver.saveNetToFile)

    ui.actionCreateNew.triggered.connect(supervisor.receiveCreateNewAction)
    ui.actionLoadFrom.triggered.connect(supervisor.receiveLoadFromAction)

    window.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
