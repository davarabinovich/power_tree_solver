
# TODO: Direct access to _forest and _electric_net can confuse, it's not understandable, which one shall be used to
#       modify the net tree

from __future__ import annotations
from typing import Optional
from math import ceil

from electric_net import *

from graph_gui import *
from graph_gui_int import *
from source_node import *
from converter_node import *
from load_node import *

from logger_if import *


# TODO: Rename load to consumer
class NetView(GraphView):
    # Public interface
    CROSS_POSITION = QPointF(20, 200)


    class NotSpecifiedParentForDeletion(Exception): pass
    class ClosingReconnection(Exception): pass


    def __init__(self, parent: QWidget=None):
        super().__init__(parent)
        self._electric_net: ElectricNet | None = None
        self._is_valid = True
        self._logger: LoggerIf | None = None

        self._is_waiting_for_node_selection = False
        self._parent_to_be_deleted: GraphNode | None = None
        self._parent_to_be_deleted_forest_node: Forest.ForestNode | None = None

        self._cur_new_power_input_number = 1
        self._cur_new_converter_number = 1
        self._cur_new_consumer_number = 1

        self._nodes = 0
        self._lines = 0


    def initNet(self):
        self._electric_net = ElectricNet()

    def setNet(self, net: ElectricNet):
        self._electric_net = net
        self.blockSignals(True)
        for input in self._electric_net.get_inputs():
            self._placeSubtree(input)
        self.blockSignals(False)

    def initView(self, logger: LoggerIf=None):
        self.init()
        self._logger = logger

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

            self._log('Delete Ancestor Reconnecting', self._parent_to_be_deleted_forest_node.content.name,
                      selected_forest_node.content.name)

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

        self._log('Add Power Input', ui_form.nameLineEdit.text())

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

        for item in source.childItems():
            if isinstance(item, QGraphicsProxyWidget):
                widget = item.widget()
                source_name = widget.ui.nameLineEdit.text()
        self._log('Add Converter', ui_form.nameLineEdit.text(), source_name)

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

        for item in source.childItems():
            if isinstance(item, QGraphicsProxyWidget):
                widget = item.widget()
                source_name = widget.ui.nameLineEdit.text()
        self._log('Add Consumer', ui_form.nameLineEdit.text(), source_name)

        self.contentChanged.emit()

    @pyqtSlot('PyQt_PyObject', 'PyQt_PyObject')
    def _deleteNode(self, graph_node: GraphNode, forest_node: Forest.ForestNode):
        if forest_node.is_leaf():
            self.deleteLeaf(graph_node)
            self._electric_net._forest.delete_leaf(forest_node)
            log_action_str = 'Delete Leaf'

        else:
            if len(self._electric_net._forest.roots) == 1 and \
               id(forest_node) == id(self._electric_net._forest.roots[0]):
                button = QMessageBox.question(self, 'There is no node to be a new parent',
                                                    'Are you sure, that you want to fully clear the net?')
                if button == QMessageBox.StandardButton.Yes:
                    self.deleteParent(graph_node)
                    self._electric_net._forest.delete_subtree(forest_node)
                return

            mode_selection_message_box = QMessageBox(QMessageBox.Icon.Question,
                                                     'The node with successors are being deleted',
                                                     'What do you want to do with successors?', parent=self)
            delete_button = mode_selection_message_box.addButton('Delete', QMessageBox.ButtonRole.NoRole)
            reconnect_button = mode_selection_message_box.addButton('Reconnect', QMessageBox.ButtonRole.NoRole)


            if forest_node.is_successor():
                promote_button = mode_selection_message_box.addButton('Promote', QMessageBox.ButtonRole.NoRole)
                cancel_button = mode_selection_message_box.addButton('', QMessageBox.ButtonRole.RejectRole)
                cancel_button.hide()
                mode_selection_message_box.exec()

                if mode_selection_message_box.clickedButton() == delete_button:
                    log_action_str = 'Delete Subtree'
                    self.deleteParent(graph_node)
                    self._electric_net._forest.delete_subtree(forest_node)
                elif mode_selection_message_box.clickedButton() == promote_button:
                    log_action_str = 'Delete Ancestor Promoting'
                    self.deleteParent(graph_node, graph_node.parentPort.multiline._parent)
                    self._electric_net._forest.cut_node(forest_node, is_needed_to_replace_node_with_successors=True)
                elif mode_selection_message_box.clickedButton() == reconnect_button:
                    self._is_waiting_for_node_selection = True
                    self._parent_to_be_deleted = graph_node
                    self._parent_to_be_deleted_forest_node = forest_node
                    return
                else:
                    return

            else:
                cancel_button = mode_selection_message_box.addButton('', QMessageBox.ButtonRole.RejectRole)
                cancel_button.hide()
                mode_selection_message_box.exec()

                if mode_selection_message_box.clickedButton() == delete_button:
                    log_action_str = 'Delete Subtree'
                    self.deleteParent(graph_node)
                    self._electric_net._forest.delete_subtree(forest_node)
                elif mode_selection_message_box.clickedButton() == reconnect_button:
                    self._is_waiting_for_node_selection = True
                    self._parent_to_be_deleted = graph_node
                    self._parent_to_be_deleted_forest_node = forest_node
                    return
                else:
                    return

        self._log(log_action_str, forest_node.content.name)

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

    def _log(self, action, *argv):
        if self._logger is None:
            return

        if self._is_valid:
            self._logger.write_action(action, *argv)
            validation_result = self._validate()
            if validation_result is not True:
                # TODO: Log error message
                self._logger.mark_as_invalid()
                self._is_valid = False

    def _validate(self):
        try:
            self._nodes = 0
            self._lines = 0

            initial_search_position = QPointF(GraphView.HORIZONTAL_INDENT, GraphView.VERTICAL_INDENT)
            graphic_roots = self._collect_graphic_roots(initial_search_position)
            if graphic_roots is None:
                return False
            total_width = self._check_siblings(graphic_roots, self._forest.roots, initial_search_position)
            if total_width is None:
                return False

            nodes_amount = len(self._get_all_items_of_type(GraphNode))
            if nodes_amount != self._nodes:
                return False

            lines_amount = len(self._get_all_items_of_type(QGraphicsLineItem))
            if lines_amount != self._lines:
                return False

            # is_scene_size_correct = self._check_scene_size()
            # if not is_scene_size_correct:
            #     return False

            are_forests_coherent = self._check_forests_coherency()
            if not are_forests_coherent:
                return False

            # is_graphic_forest_valid = self._forest.is_forest_valid()
            # if not is_graphic_forest_valid:
            #     return False
            # is_electric_forest_valid = self._electric_net._forest.is_forest_valid()
            # if not is_electric_forest_valid:
            #     return False

        except Exception as exception:
            error_message = str(type(exception)) + ': ' + str(exception)
            return error_message

        return True

    def _collect_graphic_roots(self, initial_search_position: QPointF) -> Optional[list[GraphNode]]:
        def is_search_position_out_of_scene(net_view: NetView, search_position: QPointF):
            scene_rect = net_view._scene.sceneRect()
            scene_bottom_bound = scene_rect.bottom()
            result = search_position.y() >= scene_bottom_bound
            return result

        roots = []
        search_position = initial_search_position
        while not is_search_position_out_of_scene(self, search_position):
            node = self._get_single_item_at_point_by_type(search_position, GraphNode)
            if isinstance(node, GraphNode):
                roots.append(node)
            search_position = QPointF(search_position.x(), search_position.y()+GraphView.VERTICAL_STEP)
        return roots

    def _check_siblings(self, graphic_siblings: list[GraphNode], forest_siblings: list[Forest.ForestNode],
                        initial_search_position: QPointF):
        total_width = 0
        search_position = initial_search_position
        for index in range(len(graphic_siblings)):
            graphic_sibling: GraphNode = self._get_single_item_at_point_by_type(search_position, GraphNode)
            if graphic_sibling is None:
                return None
            if id(graphic_sibling) != id(graphic_siblings[index]):
                return None

            forest_sibling = forest_siblings[index]
            width = self._check_subtree(graphic_sibling, forest_sibling)
            if width is None:
                return None
            search_position = QPointF(search_position.x(), search_position.y() + (width+1) * GraphView.VERTICAL_STEP)
            total_width += width
            index += 1

        total_width += len(graphic_siblings) - 1
        return total_width

    def _check_subtree(self, graphic_subroot: GraphNode, forest_subroot: Forest.ForestNode) -> Optional[int]:
        total_width = 0
        self._nodes += 1

        are_roots_coherent = self._check_nodes_coherency(graphic_subroot, forest_subroot)
        if not are_roots_coherent:
            return None

        subroot_parent_port = graphic_subroot.parentPort
        if subroot_parent_port:
            subroot_in_parent_line = subroot_parent_port. \
                multiline._children_ports[subroot_parent_port.portNumber-1].node
            if id(graphic_subroot) != id(subroot_in_parent_line):
                return None

            parent_branch_point = subroot_parent_port.multiline._parent.calcBranchPointForParent()
            child_line = subroot_parent_port.multiline._children_ports[subroot_parent_port.portNumber-1].line
            child_line_end = graphic_subroot.calcConnectionPointForChild()
            child_line_start = QPointF(parent_branch_point.x(), child_line_end.y())
            child_conn_point = graphic_subroot.calcConnectionPointForChild()
            child_line_search_point = QPointF(child_conn_point.x() - GraphNode.OUTLINE_THICKNESS, child_conn_point.y())

            if not self._check_line(child_line, child_line_start, child_line_end, child_line_search_point):
                return None

        subroot_children_line = graphic_subroot.childrenLine
        if subroot_children_line:
            if len(subroot_children_line._children_ports) != len(forest_subroot.successors):
                return None

            parent_line = subroot_children_line._parent_line
            parent_line_start = graphic_subroot.calcConnectionPointForParent()
            parent_line_end = graphic_subroot.calcBranchPointForParent()
            subroot_parent_conn_point = graphic_subroot.calcConnectionPointForParent()
            parent_line_search_point = QPointF(subroot_parent_conn_point.x() + GraphNode.OUTLINE_THICKNESS,
                                               subroot_parent_conn_point.y())

            if not self._check_line(parent_line, parent_line_start, parent_line_end, parent_line_search_point):
                return None

            graphic_children = []
            for port in subroot_children_line._children_ports:
                graphic_children.append(port.node)
            initial_search_position = QPointF(subroot_parent_conn_point.x() + GraphView.HORIZONTAL_GAP,
                                              subroot_parent_conn_point.y() - GraphNode.HEIGHT / 2)
            total_width = self._check_siblings(graphic_children, forest_subroot.successors, initial_search_position)
            if total_width is None:
                return None

            branch_line = subroot_children_line._branch_line
            branch_line_start = parent_line_end
            last_child_conn_point = graphic_children[-1].calcConnectionPointForChild()
            branch_line_end_x = last_child_conn_point.x() - GraphView.HORIZONTAL_GAP + ConnectionMultiline.BRANCH_INDENT
            branch_line_end = QPointF(branch_line_end_x, last_child_conn_point.y())

            # TODO: There are two cases. It needs to rework multiline code to there will be only the second case
            if len(graphic_children) == 1:
                if not self._check_line_placement(branch_line, branch_line_start, branch_line_end):
                    return None
                self._lines += 1
            else:
                branch_line_search_point = QPointF(branch_line_end_x,
                                                   last_child_conn_point.y() - GraphNode.OUTLINE_THICKNESS)
                if not self._check_line(branch_line, branch_line_start, branch_line_end, branch_line_search_point):
                    return None

        return total_width

    def _check_nodes_coherency(self, graphic_node: GraphNode, forest_node: Forest.ForestNode):
        if id(graphic_node.data(GraphView._FOREST_NODE_DATA_KEY)) != id(forest_node):
            return False
        if id(forest_node.content) != id(graphic_node):
            return False

        if forest_node.is_successor():
            graphic_parent = graphic_node.parentPort.multiline._parent
            forest_parent = forest_node.parent
            if not self._check_nodes_coherency(graphic_parent, forest_parent):
                return False

        return True

    def _get_all_items_of_type(self, type):
        items = []
        scene_items = self._scene.items()
        for item in scene_items:
            if isinstance(item, type):
                items.append(item)
        return items

    def _check_scene_size(self):
        forest_width = self._forest.calc_width()
        forest_depth = self._forest.calc_depth()
        proper_scene_right_x = GraphView.HORIZONTAL_INDENT + (forest_depth + 1) * GraphView.HORIZONTAL_STEP
        proper_scene_bottom_y = GraphView.VERTICAL_INDENT + (forest_width + 1) * GraphView.VERTICAL_STEP
        scene_rect = self._scene.sceneRect()

        if not self._are_coordinates_equal(proper_scene_right_x, scene_rect.right()):
            return False
        if not self._are_coordinates_equal(proper_scene_bottom_y, scene_rect.bottom()):
            return False
        return True

    def _check_forests_coherency(self):
        graphic_forest = self._forest
        electric_forest = self._electric_net._forest
        if len(graphic_forest.roots) != len(electric_forest.roots):
            return False

        for index in range(len(graphic_forest.roots)):
            if not self._check_subtrees_coherency(graphic_forest.roots[index], electric_forest.roots[index]):
                return False
        return True

    def _check_subtrees_coherency(self, graphic_subroot: Forest.ForestNode, electric_subroot: Forest.ForestNode):
        graphic_subroot_graph_node = graphic_subroot.content
        subroot_widget = self._get_widget(graphic_subroot_graph_node)
        electric_subroot_candidate = subroot_widget._electric_node

        if id(electric_subroot) != id (electric_subroot_candidate):
            return False
        if len(graphic_subroot.successors) != len(electric_subroot.successors):
            return False
        for index in range(len(graphic_subroot.successors)):
            if not self._check_subtrees_coherency(graphic_subroot.successors[index],
                                                  electric_subroot.successors[index]):
                return False
        return True

    def _get_widget(self, node: GraphNode) -> SourceWidget | ConverterWidget | LoadWidget | None:
        child_items = node.childItems()
        for item in child_items:
            if isinstance(item, QGraphicsProxyWidget):
                return item.widget()
        return None

    def _get_single_item_at_point_by_type(self, point: QPointF, desired_type):
        items = self._scene.items(point)
        if len(items) != 1:
            return None
        if not isinstance(items[0], desired_type):
            return None
        return items[0]

    def _check_line(self, line: QGraphicsLineItem, proper_start: QPointF, proper_end: QPointF, search_point: QPointF):
        if not self._check_line_placement(line, proper_start, proper_end):
            return False
        line_candidate = self._get_single_item_at_point_by_type(search_point, QGraphicsLineItem)
        if line_candidate is None:
            return False
        if id(line) != id(line_candidate):
            return False

        self._lines += 1
        return True

    def _check_line_placement(self, line: QGraphicsLineItem, proper_start: QPointF, proper_end: QPointF):
        qlinef = line.line()
        qlinef_p1 = line.mapToScene(qlinef.p1())
        qlinef_p2 = line.mapToScene(qlinef.p2())

        if not self._are_coordinates_equal(qlinef_p1.x(), proper_start.x()):
            return False
        if not self._are_coordinates_equal(qlinef_p1.y(), proper_start.y()):
            return False
        if not self._are_coordinates_equal(qlinef_p2.x(), proper_end.x()):
            return False
        if not self._are_coordinates_equal(qlinef_p2.y(), proper_end.y()):
            return False
        return True

    def _are_coordinates_equal(self, first, second):
        EPSILON = 0.001
        if abs(first - second) > EPSILON:
            return False
        return True


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
