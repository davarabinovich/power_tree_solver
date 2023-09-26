
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


    class NotSpecifiedParentForDeletion(Exception): pass
    class ClosingReconnection(Exception): pass


    def __init__(self, parent: QWidget=None):
        super().__init__(parent)
        self._electric_net = None
        self._is_waiting_for_node_selection = False
        self._parent_to_be_deleted: GraphNode | None = None
        self._parent_to_be_deleted_forest_node: Forest.ForestNode | None = None

        self._cur_new_power_input_number = 1
        self._cur_new_converter_number = 1
        self._cur_new_consumer_number = 1


    def initNet(self):
        self._electric_net = ElectricNet()

    def setNet(self, net: ElectricNet):
        self._electric_net = net
        self.blockSignals(True)
        for input in self._electric_net.get_inputs():
            self._placeSubtree(input)
        self.blockSignals(False)

    def initView(self):
        self.init()

        cross = self.addCross(NetView.CROSS_POSITION)
        cross.clicked.connect(self._addInput)

        self._is_waiting_for_node_selection = False
        self._parent_to_be_deleted: GraphNode | None = None
        self._parent_to_be_deleted_forest_node: Forest.ForestNode | None = None

        self._cur_new_power_input_number = 1
        self._cur_new_converter_number = 1
        self._cur_new_consumer_number = 1

    contentChanged = pyqtSignal(name='contentChanged')

    @pyqtSlot('PyQt_PyObject')
    def nodeSelected(self, selected_node: GraphNode):
        def is_reconnection_correct(new_parent: Node):
            result = True
            if new_parent.content.type == ElectricNodeType.LOAD:
                result = False
            elif self._parent_to_be_deleted_forest_node.is_ancestor(new_parent):
                result = False
            return result

        if self._is_waiting_for_node_selection:
            if self._parent_to_be_deleted is None:
                raise NetView.NotSpecifiedParentForDeletion

            for child_item in selected_node.childItems():
                if isinstance(child_item, QGraphicsProxyWidget):
                    widget = child_item.widget()
                    selected_forest_node = widget.electric_node

            if not is_reconnection_correct(selected_forest_node):
                message_box_title = 'Incorrect choice of new parent'
                if selected_forest_node.content.type == ElectricNodeType.LOAD:
                    message_box_text = 'A consumer cannot be a parent'
                else:
                    message_box_text = 'Successor of a deleting node cannot be a new parent'

                QMessageBox.critical(self, message_box_title, message_box_text)
                self._is_waiting_for_node_selection = False
                self._parent_to_be_deleted = None
                self._parent_to_be_deleted_forest_node = None
                return


            self.deleteParent(self._parent_to_be_deleted, selected_node)
            self._electric_net._forest.move_subtree(self._parent_to_be_deleted_forest_node, selected_forest_node)
            self._electric_net._forest.cut_node(self._parent_to_be_deleted_forest_node)

            self._is_waiting_for_node_selection = False
            self._parent_to_be_deleted = None
            self._parent_to_be_deleted_forest_node = None

            self.contentChanged.emit()

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
                if widget.ui.nameLineEdit.text != '':
                    name = subroot.content.name
                else:
                    if isinstance(widget, SourceWidget):
                        name = 'Input ' + str(self._cur_new_power_input_number)
                        self._cur_new_power_input_number += 1
                    elif isinstance(widget, ConverterWidget):
                        name = 'Converter ' + str(self._cur_new_converter_number)
                        self._cur_new_converter_number += 1
                    else:
                        name = 'Consumer ' + str(self._cur_new_consumer_number)
                        self._cur_new_consumer_number += 1
                widget.ui.nameLineEdit.setText(name)

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

        input.clicked.connect(self.nodeSelected)
        input.sideWidgetClicked.connect(widget._receiveNodeSideWidgetClick)
        widget.deleted.connect(self._deleteNode)
        widget.converterAdded.connect(self._addConverter)
        widget.loadAdded.connect(self._addLoad)
        ui_form.valueLineEdit.textChanged.connect(widget.changeValue)
        ui_form.valueLineEdit.textChanged.connect(self.contentChanged)
        ui_form.nameLineEdit.textChanged.connect(widget.changeName)
        ui_form.nameLineEdit.textChanged.connect(self.contentChanged)

        return input

    def placeConverter(self, node: Forest.ForestNode, source: GraphNode) -> GraphNode:
        widget, ui_form = NetView._prepareConverterWidget()
        side_widgets = NetView._prepareSourceSideWidgets()
        converter = self.addChild(source, widget, side_widgets)
        widget.electric_node = node

        converter.clicked.connect(self.nodeSelected)
        converter.sideWidgetClicked.connect(widget._receiveNodeSideWidgetClick)
        widget.deleted.connect(self._deleteNode)
        widget.converterAdded.connect(self._addConverter)
        widget.loadAdded.connect(self._addLoad)
        ui_form.valueLineEdit.textChanged.connect(widget.changeValue)
        ui_form.valueLineEdit.textChanged.connect(self.contentChanged)
        ui_form.nameLineEdit.textChanged.connect(widget.changeName)
        ui_form.nameLineEdit.textChanged.connect(self.contentChanged)
        ui_form.linearRadioButton.toggled.connect(widget.changeType)
        ui_form.linearRadioButton.toggled.connect(self.contentChanged)

        return converter

    def placeLoad(self, node: Forest.ForestNode, source: GraphNode) -> GraphNode:
        widget, ui_form = NetView._prepareLoadWidget()
        side_widgets = NetView._prepareConsumerSideWidgets()
        load = self.addChild(source, widget, side_widgets)
        widget.electric_node = node

        load.clicked.connect(self.nodeSelected)
        load.sideWidgetClicked.connect(widget._receiveNodeSideWidgetClick)
        widget.deleted.connect(self._deleteNode)
        ui_form.valueLineEdit.textChanged.connect(widget.changeValue)
        ui_form.valueLineEdit.textChanged.connect(self.contentChanged)
        ui_form.nameLineEdit.textChanged.connect(widget.changeName)
        ui_form.nameLineEdit.textChanged.connect(self.contentChanged)
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

        input.clicked.connect(self.nodeSelected)
        input.sideWidgetClicked.connect(widget._receiveNodeSideWidgetClick)
        widget.deleted.connect(self._deleteNode)
        widget.converterAdded.connect(self._addConverter)
        widget.loadAdded.connect(self._addLoad)
        ui_form.valueLineEdit.textChanged.connect(widget.changeValue)
        ui_form.valueLineEdit.textChanged.connect(self.contentChanged)
        ui_form.nameLineEdit.textChanged.connect(widget.changeName)
        ui_form.nameLineEdit.textChanged.connect(self.contentChanged)

        name = 'Input ' + str(self._cur_new_power_input_number)
        self._cur_new_power_input_number += 1
        ui_form.nameLineEdit.setText(name)

        # TODO: Do using decorators
        self.contentChanged.emit()

    @pyqtSlot('PyQt_PyObject', 'PyQt_PyObject')
    def _addConverter(self, source: GraphNode, parent: Forest.ForestNode):
        widget, ui_form = NetView._prepareConverterWidget()
        side_widgets = NetView._prepareSourceSideWidgets()
        converter = self.addChild(source, widget, side_widgets)
        new_converter = self._electric_net.add_converter(parent)
        widget.electric_node = new_converter

        converter.clicked.connect(self.nodeSelected)
        converter.sideWidgetClicked.connect(widget._receiveNodeSideWidgetClick)
        widget.deleted.connect(self._deleteNode)
        widget.converterAdded.connect(self._addConverter)
        widget.loadAdded.connect(self._addLoad)
        ui_form.valueLineEdit.textChanged.connect(widget.changeValue)
        ui_form.valueLineEdit.textChanged.connect(self.contentChanged)
        ui_form.nameLineEdit.textChanged.connect(widget.changeName)
        ui_form.nameLineEdit.textChanged.connect(self.contentChanged)
        ui_form.linearRadioButton.toggled.connect(widget.changeType)
        ui_form.linearRadioButton.toggled.connect(self.contentChanged)

        name = 'Converter ' + str(self._cur_new_converter_number)
        self._cur_new_converter_number += 1
        ui_form.nameLineEdit.setText(name)

        self.contentChanged.emit()

    @pyqtSlot('PyQt_PyObject', 'PyQt_PyObject')
    def _addLoad(self, source: GraphNode, parent: Forest.ForestNode):
        widget, ui_form = NetView._prepareLoadWidget()
        side_widgets = NetView._prepareConsumerSideWidgets()
        consumer = self.addChild(source, widget, side_widgets)
        new_load = self._electric_net.add_load(parent)
        widget.electric_node = new_load

        consumer.clicked.connect(self.nodeSelected)
        consumer.sideWidgetClicked.connect(widget._receiveNodeSideWidgetClick)
        widget.deleted.connect(self._deleteNode)
        ui_form.valueLineEdit.textChanged.connect(widget.changeValue)
        ui_form.valueLineEdit.textChanged.connect(self.contentChanged)
        ui_form.nameLineEdit.textChanged.connect(widget.changeName)
        ui_form.nameLineEdit.textChanged.connect(self.contentChanged)
        ui_form.currentRadioButton.toggled.connect(widget.changeType)
        ui_form.currentRadioButton.toggled.connect(self.contentChanged)

        name = 'Consumer ' + str(self._cur_new_consumer_number)
        self._cur_new_consumer_number += 1
        ui_form.nameLineEdit.setText(name)

        self.contentChanged.emit()

    @pyqtSlot('PyQt_PyObject', 'PyQt_PyObject')
    def _deleteNode(self, graph_node: GraphNode, forest_node: Forest.ForestNode):
        if forest_node.is_leaf():
            self.deleteLeaf(graph_node)
            self._electric_net._forest.delete_leaf(forest_node)

        else:
            if len(self._electric_net._forest.roots) == 1 and \
               id(forest_node) == id(self._electric_net._forest.roots[0]):
                button = QMessageBox.question(self, 'There is no node to be a new parent',
                                                    'Are you sure, that you want to fully clear the net?')
                if button == QMessageBox.StandardButton.Yes:
                    self.deleteParent(graph_node)
                    self._electric_net._forest.delete_subtree(forest_node)
                return

            mode_selection_message_box = QMessageBox(self)
            mode_selection_message_box.setWindowTitle('The node with successors are being deleted')
            mode_selection_message_box.setText('What do you want to do with successors?')
            delete_button = mode_selection_message_box.addButton('Delete', QMessageBox.ButtonRole.NoRole)
            mode_selection_message_box.addButton('Reconnect', QMessageBox.ButtonRole.NoRole)

            if forest_node.is_successor():
                promote_button = mode_selection_message_box.addButton('Promote', QMessageBox.ButtonRole.NoRole)
                mode_selection_message_box.exec()
                if mode_selection_message_box.clickedButton() == delete_button:
                    self.deleteParent(graph_node)
                    self._electric_net._forest.delete_subtree(forest_node)
                elif mode_selection_message_box.clickedButton() == promote_button:
                    self.deleteParent(graph_node, graph_node.parentPort.multiline._parent)
                    self._electric_net._forest.cut_node(forest_node, is_needed_to_replace_node_with_successors=True)
                else:
                    self._is_waiting_for_node_selection = True
                    self._parent_to_be_deleted = graph_node
                    self._parent_to_be_deleted_forest_node = forest_node
                    return

            else:
                mode_selection_message_box.exec()
                if mode_selection_message_box.clickedButton() == delete_button:
                    self.deleteParent(graph_node)
                    self._electric_net._forest.delete_subtree(forest_node)
                else:
                    self._is_waiting_for_node_selection = True
                    self._parent_to_be_deleted = graph_node
                    self._parent_to_be_deleted_forest_node = forest_node
                    return

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
        "Delete": 0,
        "Converter": 1,
        "Load": 2
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
        input_ui.nameLineEdit.setPalette(palette)

        # TODO: app is falling, when already inputed number are fully cleared
        input_ui.valueLineEdit.setValidator(QDoubleValidator())

        return widget, input_ui

    @staticmethod
    def _prepareSourceSideWidgets() -> list:
        delete_cross = CrossIcon(label='Delete')
        add_converter_cross = PlusIcon(label="Add Converter")
        add_load_cross = PlusIcon(label="Add Load")
        side_widgets = [delete_cross, add_converter_cross, add_load_cross]
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
        converter_ui.nameLineEdit.setPalette(palette)

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
        load_ui.nameLineEdit.setPalette(palette)

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
    deleted = pyqtSignal('PyQt_PyObject', 'PyQt_PyObject', name='deleted')

    @pyqtSlot(str)
    def changeName(self, text: str):
        if text != '':
            new_value = text
        else:
            new_value = None
        self._electric_node.content.name = new_value

    @pyqtSlot(str)
    def changeValue(self, text: str):
        if text != '':
            new_value = float(text.replace(',', '.'))
        else:
            new_value = 0
        self._electric_node.content.value = new_value

    @pyqtSlot('PyQt_PyObject', int)
    def _receiveNodeSideWidgetClick(self, source: QGraphicsItem, side_widget_num):
        if side_widget_num == NetView._SIDE_WIDGET_KEYS["Delete"]:
            self.deleted.emit(source, self._electric_node)
        elif side_widget_num == NetView._SIDE_WIDGET_KEYS["Converter"]:
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
    deleted = pyqtSignal('PyQt_PyObject', 'PyQt_PyObject', name='deleted')

    @pyqtSlot(str)
    def changeName(self, text: str):
        if text != '':
            new_value = text
        else:
            new_value = None
        self._electric_node.content.name = new_value

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
        if side_widget_num == NetView._SIDE_WIDGET_KEYS["Delete"]:
            self.deleted.emit(source, self._electric_node)
        elif side_widget_num == NetView._SIDE_WIDGET_KEYS["Converter"]:
            self.converterAdded.emit(source, self._electric_node)
        else:
            self.loadAdded.emit(source, self._electric_node)


class LoadWidget(QWidget):
    _TYPE_BUTTON_IDS = {
        "Constant Current": 1,
        "Resistive": 2
    }

    def __init__(self, ui_form: Ui_LoadWidget):
        super().__init__()
        self.ui = ui_form
        self._electric_node = None

    @pyqtSlot(str)
    def changeName(self, text: str):
        if text != '':
            new_value = text
        else:
            new_value = None
        self._electric_node.content.name = new_value

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
        if side_widget_num == NetView._SIDE_WIDGET_KEYS["Delete"]:
            self.deleted.emit(source, self._electric_node)
