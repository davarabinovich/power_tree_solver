
# TODO: Direct access to _forest and _electric_net can confuse, it's not understandable, which one shall be used to
#       modify the net tree

from __future__ import annotations

from electric_net import *
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
        self._electric_net = ElectricNet()
        self._addInput()

    @property
    def electric_net(self):
        return self._electric_net

    # Private part
    @pyqtSlot()
    def _addInput(self):
        widget, ui_form = NetView._prepareSourceWidget()
        side_widgets = NetView._prepareSourceSideWidgets()
        input = self.addRoot(widget, side_widgets)
        new_input = self._electric_net.create_input()
        widget.electric_node = new_input

        input.sideWidgetClicked.connect(widget._receiveNodeSideWidgetClick)
        widget.converterAdded.connect(self._addConverter)
        widget.loadAdded.connect(self._addLoad)
        ui_form.valueLineEdit.textChanged.connect(widget.changeValue)

    @pyqtSlot('PyQt_PyObject', 'PyQt_PyObject')
    def _addConverter(self, source: GraphNode, parent: Forest.ForestNode):
        widget, ui_form = NetView._prepareSourceWidget()
        side_widgets = NetView._prepareSourceSideWidgets()
        converter = self.addChild(source, widget, side_widgets)
        new_converter = self._electric_net.add_converter(parent)
        widget.electric_node = new_converter

        converter.sideWidgetClicked.connect(widget._receiveNodeSideWidgetClick)
        widget.converterAdded.connect(self._addConverter)
        widget.loadAdded.connect(self._addLoad)
        ui_form.valueLineEdit.textChanged.connect(widget.changeValue)

    def _addLoad(self, source: GraphNode, parent: Forest.ForestNode):
        widget, ui_form = NetView._prepareLoadWidget()
        self.addChild(source, widget)
        new_load = self._electric_net.add_load(parent)
        widget.electric_node = new_load
        ui_form.valueLineEdit.textChanged.connect(widget.changeValue)

    _SIDE_WIDGET_KEYS = {
        "Converter": 0,
        "Load": 1
    }

    @staticmethod
    def _prepareSourceWidget() -> tuple[SourceWidget, Ui_SourceWidget]:
        input_ui = Ui_SourceWidget()
        widget = SourceWidget()
        palette = QPalette(GraphNode.FILLING_COLOR)
        widget.setPalette(palette)
        input_ui.setupUi(widget)

        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Base, QColorConstants.White)
        palette.setColor(QPalette.ColorRole.Text, QColorConstants.Black)
        input_ui.valueLineEdit.setPalette(palette)

        # TODO: app is falling, when already inputed number are fully cleared
        input_ui.valueLineEdit.setValidator(QDoubleValidator())

        return widget, input_ui

    @staticmethod
    def _prepareSourceSideWidgets() -> list:
        add_converter_cross = CrossIcon(label="Add Converter")
        add_load_cross = CrossIcon(label="Add Load")
        side_widgets = [add_converter_cross, add_load_cross]
        return side_widgets

    @staticmethod
    def _prepareLoadWidget() -> tuple[LoadWidget, Ui_LoadWidget]:
        load_ui = Ui_LoadWidget()
        widget = LoadWidget()
        palette = QPalette(GraphNode.FILLING_COLOR)
        widget.setPalette(palette)
        load_ui.setupUi(widget)

        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Base, QColorConstants.White)
        palette.setColor(QPalette.ColorRole.Text, QColorConstants.Black)
        load_ui.valueLineEdit.setPalette(palette)

        return widget, load_ui


class SourceWidget(QWidget):
    def __init__(self):
        super().__init__()
        self._electric_node = None

    @property
    def electric_node(self) -> Forest.ForestNode:
        return self._electric_node
    @electric_node.setter
    def electric_node(self, value: Forest.ForestNode):
        self._electric_node = value

    converterAdded = pyqtSignal('PyQt_PyObject', 'PyQt_PyObject', name='converterAdded')
    loadAdded = pyqtSignal('PyQt_PyObject', 'PyQt_PyObject', name='loadAdded')

    @pyqtSlot(str)
    def changeValue(self, text: str):
        print(text)
        self._electric_node.content.value = float(text)

    @pyqtSlot('PyQt_PyObject', int)
    def _receiveNodeSideWidgetClick(self, source: QGraphicsItem, side_widget_num):
        if side_widget_num == NetView._SIDE_WIDGET_KEYS["Converter"]:
            self.converterAdded.emit(source, self._electric_node)
        else:
            self.loadAdded.emit(source, self._electric_node)


class LoadWidget(QWidget):
    def __init__(self):
        super().__init__()
        self._electric_node = None

    @property
    def electric_node(self) -> Forest.ForestNode:
        return self._electric_node
    @electric_node.setter
    def electric_node(self, value: Forest.ForestNode):
        self._electric_node = value

    @pyqtSlot(str)
    def changeValue(self, text: str):
        print(text)
        self._electric_node.content.value = float(text)
