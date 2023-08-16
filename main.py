
import sys
from PyQt6.QtWidgets import QApplication
from common_gui import *


VERSION = (0, 1, "alfa")


def main():
    app = QApplication(sys.argv)
    ui = CommonGui(app)
    ui.launch()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
