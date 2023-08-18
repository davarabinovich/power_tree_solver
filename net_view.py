
from __future__ import annotations
from graph_gui import *
from graph_gui_int import *
from source_node import *


class NetView(GraphView):
    # Public interface
    CROSS_POSITION = QPointF(20, 200)

    def __init__(self, parent: QWidget=None):
        super().__init__(parent)
        cross = self.addCross(NetView.CROSS_POSITION)
        cross.clicked.connect(self.addInput)
        self.addInput()

    @pyqtSlot()
    def addInput(self):
        widget = NetView._prepareSourceWidget()
        side_widgets = NetView._prepareSourceSideWidgets()
        self.addRoot(widget, side_widgets)


    # Private part
    @staticmethod
    def _prepareSourceWidget() -> SourceWidget:
        input_ui = Ui_SourceWidget()
        widget = SourceWidget()
        palette = QPalette(GraphNode.FILLING_COLOR)
        widget.setPalette(palette)
        input_ui.setupUi(widget)

        return widget

    @staticmethod
    def _prepareSourceSideWidgets() -> list:
        add_converter_cross = CrossIcon(label="Add Converter")
        add_load_cross = CrossIcon(label="Add Load")
        side_widgets = [add_converter_cross, add_load_cross]
        return side_widgets


class SourceWidget(QWidget):
    def __init__(self):
        super().__init__()
