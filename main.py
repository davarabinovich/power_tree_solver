
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow
from main_window import Ui_MainWindow


VERSION = (0, 1, "alfa")


def main():
    app = QApplication(sys.argv)
    window = QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(window)

    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
