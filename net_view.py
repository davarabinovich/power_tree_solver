
# TODO: Direct access to _forest and _electric_net can confuse, it's not understandable, which one shall be used to
#       modify the net tree

from __future__ import annotations

from electric_net import *
from graph_gui import *
from graph_gui_int import *
from source_node import *
from converter_node import *
from load_node import *


# TODO: Rename load to consumer
class NetView(GraphView):
    # Public interface
    CROSS_POSITION = QPointF(20, 200)

    def __init__(self, parent: QWidget=None):
        super().__init__(parent)
        self._electric_net = None

    def initNet(self):
        self._electric_net = ElectricNet()

    def setNet(self, net: ElectricNet):
        self._electric_net = net
        self.blockSignals(True)
        for input in self._electric_net.get_inputs():
            self._placeSubtree(input)
        self.blockSignals(False)

    def initView(self):
        cross = self.addCross(NetView.CROSS_POSITION)
        cross.clicked.connect(self._addInput)

    contentChanged = pyqtSignal(name='contentChanged')

    @property
    def electric_net(self):
        return self._electric_net

    # Private part
    def _placeSubtree(self, subroot: Forest.ForestNode, parent_graph_node: GraphNode | None = None):
        subroot_data: ElectricNode = subroot.content
        if subroot_data.type == ElectricNodeType.INPUT:
            graph_node = self.placeInput(subroot)
        elif subroot_data.type == ElectricNodeType.CONVERTER:
            graph_node = self.placeConverter(subroot, parent_graph_node)
        else:
            graph_node = self.placeLoad(subroot, parent_graph_node)

        for child_item in graph_node.childItems():
            if isinstance(child_item, QGraphicsProxyWidget):
                widget = child_item.widget()
                widget.ui.valueLineEdit.setText(str(subroot.content.value))
                if not isinstance(widget, LoadWidget):
                    widget.ui.loadValueLabel.setText(str(subroot.content.load))
                    if isinstance(widget, ConverterWidget):
                        if subroot.content.converter_type == ConverterType.SWITCHING:
                            widget.ui.switchingRadioButton.setEnabled(True)
                        else:
                            widget.ui.linearRadioButton.setEnabled(True)
                else:
                    if subroot.content.consumer_type == ConsumerType.CONSTANT_CURRENT:
                        widget.ui.currentRadioButton.setEnabled(True)
                    else:
                        widget.ui.resistiveRadioButton.setEnabled(True)

        # TODO: Neet to eliminate term 'input'
        for sink in self._electric_net.get_sinks(subroot):
            self._placeSubtree(sink, graph_node)

    def placeInput(self, node: Forest.ForestNode) -> GraphNode:
        widget, ui_form = NetView._prepareSourceWidget()
        side_widgets = NetView._prepareSourceSideWidgets()
        input = self.addRoot(widget, side_widgets)
        widget.electric_node = node

        input.sideWidgetClicked.connect(widget._receiveNodeSideWidgetClick)
        widget.converterAdded.connect(self._addConverter)
        widget.loadAdded.connect(self._addLoad)
        ui_form.valueLineEdit.textChanged.connect(widget.changeValue)
        ui_form.valueLineEdit.textChanged.connect(self.contentChanged)

        return input

    def placeConverter(self, node: Forest.ForestNode, source: GraphNode) -> GraphNode:
        widget, ui_form = NetView._prepareConverterWidget()
        side_widgets = NetView._prepareSourceSideWidgets()
        converter = self.addChild(source, widget, side_widgets)
        widget.electric_node = node

        converter.sideWidgetClicked.connect(widget._receiveNodeSideWidgetClick)
        widget.converterAdded.connect(self._addConverter)
        widget.loadAdded.connect(self._addLoad)
        ui_form.valueLineEdit.textChanged.connect(widget.changeValue)
        ui_form.valueLineEdit.textChanged.connect(self.contentChanged)
        ui_form.linearRadioButton.toggled.connect(widget.changeType)
        ui_form.linearRadioButton.toggled.connect(self.contentChanged)

        return converter

    def placeLoad(self, node: Forest.ForestNode, source: GraphNode) -> GraphNode:
        widget, ui_form = NetView._prepareLoadWidget()
        side_widgets = NetView._prepareConsumerSideWidgets()
        load = self.addChild(source, widget, side_widgets)
        widget.electric_node = node

        load.sideWidgetClicked.connect(widget._receiveNodeSideWidgetClick)
        widget.deleted.connect(self._deleteNode)
        ui_form.valueLineEdit.textChanged.connect(widget.changeValue)
        ui_form.valueLineEdit.textChanged.connect(self.contentChanged)
        ui_form.currentRadioButton.toggled.connect(widget.changeType)
        ui_form.currentRadioButton.toggled.connect(self.contentChanged)

        return load

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
        ui_form.valueLineEdit.textChanged.connect(self.contentChanged)

        # TODO: Do using decorators
        self.contentChanged.emit()

    @pyqtSlot('PyQt_PyObject', 'PyQt_PyObject')
    def _addConverter(self, source: GraphNode, parent: Forest.ForestNode):
        widget, ui_form = NetView._prepareConverterWidget()
        side_widgets = NetView._prepareSourceSideWidgets()
        converter = self.addChild(source, widget, side_widgets)
        new_converter = self._electric_net.add_converter(parent)
        widget.electric_node = new_converter

        converter.sideWidgetClicked.connect(widget._receiveNodeSideWidgetClick)
        widget.converterAdded.connect(self._addConverter)
        widget.loadAdded.connect(self._addLoad)
        ui_form.valueLineEdit.textChanged.connect(widget.changeValue)
        ui_form.valueLineEdit.textChanged.connect(self.contentChanged)
        ui_form.linearRadioButton.toggled.connect(widget.changeType)
        ui_form.linearRadioButton.toggled.connect(self.contentChanged)

        self.contentChanged.emit()

    @pyqtSlot('PyQt_PyObject', 'PyQt_PyObject')
    def _addLoad(self, source: GraphNode, parent: Forest.ForestNode):
        widget, ui_form = NetView._prepareLoadWidget()
        side_widgets = NetView._prepareConsumerSideWidgets()
        consumer = self.addChild(source, widget, side_widgets)
        new_load = self._electric_net.add_load(parent)
        widget.electric_node = new_load

        consumer.sideWidgetClicked.connect(widget._receiveNodeSideWidgetClick)
        widget.deleted.connect(self._deleteNode)
        ui_form.valueLineEdit.textChanged.connect(widget.changeValue)
        ui_form.valueLineEdit.textChanged.connect(self.contentChanged)
        ui_form.currentRadioButton.toggled.connect(widget.changeType)
        ui_form.currentRadioButton.toggled.connect(self.contentChanged)

        self.contentChanged.emit()

    @pyqtSlot('PyQt_PyObject', 'PyQt_PyObject')
    def _deleteNode(self, graph_node: GraphNode, forest_node: Forest.ForestNode):
        self.deleteNode(graph_node)
        self._electric_net.delete_load(forest_node)
        self.contentChanged.emit()

    # TODO: Very ugly
    @pyqtSlot()
    def updateLoads(self):
        items = self._scene.items()
        for item in items:
            if isinstance(item, GraphNode):
                child_items = item.childItems()
                for child_item in child_items:
                    if isinstance(child_item, QGraphicsProxyWidget):
                        widget = child_item.widget()
                        if isinstance(widget, SourceWidget) or isinstance(widget, ConverterWidget):
                            widget_node_data: ElectricNode = widget.electric_node.content
                            widget.ui.loadValueLabel.setText(str(widget_node_data.load))

    _SIDE_WIDGET_KEYS = {
        "Converter": 0,
        "Load": 1
    }

    @staticmethod
    def _prepareSourceWidget() -> tuple[SourceWidget, Ui_SourceWidget]:
        input_ui = Ui_SourceWidget()
        widget = SourceWidget(input_ui)
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
        add_converter_cross = PlusIcon(label="Add Converter")
        add_load_cross = PlusIcon(label="Add Load")
        side_widgets = [add_converter_cross, add_load_cross]
        return side_widgets

    @staticmethod
    def _prepareConsumerSideWidgets() -> list[SideWidget]:
        delete_cross = CrossIcon(label='Delete')
        side_widgets = [delete_cross]
        return side_widgets

    @staticmethod
    def _prepareConverterWidget() -> tuple[ConverterWidget, Ui_ConverterWidget]:
        converter_ui = Ui_ConverterWidget()
        widget = ConverterWidget(converter_ui)
        palette = QPalette(GraphNode.FILLING_COLOR)
        widget.setPalette(palette)
        converter_ui.setupUi(widget)

        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Base, QColorConstants.White)
        palette.setColor(QPalette.ColorRole.Text, QColorConstants.Black)
        converter_ui.valueLineEdit.setPalette(palette)

        # TODO: app is falling, when already inputed number are fully cleared
        converter_ui.valueLineEdit.setValidator(QDoubleValidator())

        return widget, converter_ui

    @staticmethod
    def _prepareLoadWidget() -> tuple[LoadWidget, Ui_LoadWidget]:
        load_ui = Ui_LoadWidget()
        widget = LoadWidget(load_ui)
        palette = QPalette(GraphNode.FILLING_COLOR)
        widget.setPalette(palette)
        load_ui.setupUi(widget)

        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Base, QColorConstants.White)
        palette.setColor(QPalette.ColorRole.Text, QColorConstants.Black)
        load_ui.valueLineEdit.setPalette(palette)

        load_ui.valueLineEdit.setValidator(QDoubleValidator())

        return widget, load_ui


class SourceWidget(QWidget):
    def __init__(self, ui_form: Ui_SourceWidget):
        super().__init__()
        self.ui = ui_form
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
        if text != '':
            new_value = float(text.replace(',', '.'))
        else:
            new_value = 0
        self._electric_node.content.value = new_value

    @pyqtSlot('PyQt_PyObject', int)
    def _receiveNodeSideWidgetClick(self, source: QGraphicsItem, side_widget_num):
        if side_widget_num == NetView._SIDE_WIDGET_KEYS["Converter"]:
            self.converterAdded.emit(source, self._electric_node)
        else:
            self.loadAdded.emit(source, self._electric_node)


class ConverterWidget(QWidget):
    _TYPE_BUTTON_IDS = {
        "Linear": 1,
        "Converter": 2
    }

    def __init__(self, ui_form: Ui_ConverterWidget):
        super().__init__()
        self.ui = ui_form
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
        if text != '':
            new_value = float(text.replace(',', '.'))
        else:
            new_value = 0
        self._electric_node.content.value = new_value

    @pyqtSlot(bool)
    def changeType(self, is_linear_button_checked: bool):
        if is_linear_button_checked is True:
            self._electric_node.content.converter_type = ConverterType.LINEAR
        else:
            self._electric_node.content.converter_type = ConverterType.SWITCHING

    @pyqtSlot('PyQt_PyObject', int)
    def _receiveNodeSideWidgetClick(self, source: QGraphicsItem, side_widget_num):
        if side_widget_num == NetView._SIDE_WIDGET_KEYS["Converter"]:
            self.converterAdded.emit(source, self._electric_node)
        else:
            self.loadAdded.emit(source, self._electric_node)


class LoadWidget(QWidget):
    _SIDE_WIDGET_KEYS = {
        "Delete": 0
    }

    _TYPE_BUTTON_IDS = {
        "Constant Current": 1,
        "Resistive": 2
    }

    def __init__(self, ui_form: Ui_LoadWidget):
        super().__init__()
        self.ui = ui_form
        self._electric_node = None

    @property
    def electric_node(self) -> Forest.ForestNode:
        return self._electric_node
    @electric_node.setter
    def electric_node(self, value: Forest.ForestNode):
        self._electric_node = value

    deleted = pyqtSignal('PyQt_PyObject', 'PyQt_PyObject', name='deleted')

    @pyqtSlot(str)
    def changeValue(self, text: str):
        if text != '':
            # TODO: When enter has been pressed, written number with a comma becomes an exp form number,
            #       crush when dot is entered
            new_value = float(text.replace(',', '.'))
        else:
            new_value = 0
        self._electric_node.content.value = new_value

    @pyqtSlot(bool)
    def changeType(self, is_current_button_checked: bool):
        if is_current_button_checked is True:
            self._electric_node.content.consumer_type = ConsumerType.CONSTANT_CURRENT
        else:
            self._electric_node.content.consumer_type = ConsumerType.RESISTIVE

    @pyqtSlot('PyQt_PyObject', int)
    def _receiveNodeSideWidgetClick(self, source: QGraphicsItem, side_widget_num):
        if side_widget_num == LoadWidget._SIDE_WIDGET_KEYS["Delete"]:
            self.deleted.emit(source, self._electric_node)
