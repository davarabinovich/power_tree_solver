
import sys
from PyQt6.QtWidgets import QApplication
from gui import *


VERSION = (0, 1, "alfa")


def main():
    app = QApplication(sys.argv)
    ui = Gui()
    ui.launch()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
