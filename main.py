
import sys
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from app_config import *
from gui import *


VERSION = (0, 1, "alfa")


class TestExtern(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)

    def __del__(self):
        print("External deleted")

    @pyqtSlot()
    def slot(self):
        print("Captured external")

def main():
    app = QApplication(sys.argv)

    window = QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(window)
    test_extern = TestExtern()
    test_intern = config(ui, test_extern)
    # config(ui, test_extern)
    window.show()
    # ui.actionSaveAs.triggered.connect(test.slot)
    # gui = Gui(main_window)
    # gui.launch()

    # window = QMainWindow()
    # ui = Ui_MainWindow()ow
    # ui.setupUi(window)
    #
    # test = Test()
    # ui.actionSaveAs.triggered.connect(test.slot)

    # window.show()
#    solving_thread.start()
    sys.exit(app.exec())



if __name__ == '__main__':
    main()
