
from __future__ import annotations
from graph_gui import *
from graph_gui_int import *
from source_node import *
from load_node import *


class NetView(GraphView):
    # Public interface
    CROSS_POSITION = QPointF(20, 200)

    def __init__(self, parent: QWidget=None):
        super().__init__(parent)
        cross = self.addCross(NetView.CROSS_POSITION)
        cross.clicked.connect(self._addInput)
        self._addInput()


    # Private part
    @pyqtSlot()
    def _addInput(self):
        widget = NetView._prepareSourceWidget()
        side_widgets = NetView._prepareSourceSideWidgets()
        input = self.addRoot(widget, side_widgets)
        input.sideWidgetClicked.connect(self._receiveNodeSideWidgetClick)

    def _addConverter(self, parent: QGraphicsItem):
        widget = NetView._prepareSourceWidget()
        side_widgets = NetView._prepareSourceSideWidgets()
        converter = self.addChild(parent, widget, side_widgets)
        converter.sideWidgetClicked.connect(self._receiveNodeSideWidgetClick)

    def _addLoad(self, parent: QGraphicsItem):
        widget = NetView._prepareLoadWidget()
        load = self.addChild(parent, widget)
        load.sideWidgetClicked.connect(self._receiveNodeSideWidgetClick)

    @pyqtSlot(QGraphicsItem, int)
    def _receiveNodeSideWidgetClick(self, source: QGraphicsItem, side_widget_num):
        if side_widget_num == NetView._SIDE_WIDGET_KEYS["Converter"]:
            self._addConverter(source)
        else:
            self._addLoad(source)

    _SIDE_WIDGET_KEYS = {
        "Converter": 0,
        "Load": 1
    }

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

    @staticmethod
    def _prepareLoadWidget() -> LoadWidget:
        input_ui = Ui_LoadWidget()
        widget = LoadWidget()
        palette = QPalette(GraphNode.FILLING_COLOR)
        widget.setPalette(palette)
        input_ui.setupUi(widget)

        return widget


class SourceWidget(QWidget):
    def __init__(self):
        super().__init__()

class LoadWidget(QWidget):
    def __init__(self):
        super().__init__()
