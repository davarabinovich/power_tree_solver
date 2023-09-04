
from PyQt6.QtCore import *
from electric_net import *


class FileSaver(QObject):
    def __init__(self, parent: QObject=None):
        super().__init__(parent)

    @pyqtSlot(str)
    def saveNet(self, net_file: str):
        file = open(net_file, 'w')
        file.write('strsdf\n\nwerr')

    def _record_subtree(self, subroot: Forest.ForestNode):
        pass
