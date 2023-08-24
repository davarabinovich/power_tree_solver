
from PyQt6.QtCore import *
from electric_net import *


class FileSaver(QObject):
    def __init__(self, parent: QObject=None):
        super().__init__(parent)

    @pyqtSlot('PyQt_PyObject')
    def saveNet(self, net: ElectricNet):
        file = open('electric_net.ens', 'w')

        inputs = net.get_inputs()
        for cur_input in inputs:
            self._record_subtree(cur_input)

    def _record_subtree(self, subroot: Forest.ForestNode):
        pass
