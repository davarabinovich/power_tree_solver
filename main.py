
import sys
from PyQt6.QtWidgets import QApplication
from app_config import *
from gui import *


VERSION = (0, 1, "alfa")


def main():
    app = QApplication(sys.argv)
    main_window, solution_thread = config()
    gui = Gui(main_window)
    gui.launch()
    solution_thread.start()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
