# Form implementation generated from reading ui file 'source_node.ui'
#
# Created by: PyQt6 UI code generator 6.5.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_SourceWidget(object):
    def setupUi(self, SourceWidget):
        SourceWidget.setObjectName("SourceWidget")
        SourceWidget.resize(181, 97)
        self.valueLineEdit = QtWidgets.QLineEdit(parent=SourceWidget)
        self.valueLineEdit.setGeometry(QtCore.QRect(60, 40, 111, 20))
        self.valueLineEdit.setObjectName("valueLineEdit")
        self.valueLabel = QtWidgets.QLabel(parent=SourceWidget)
        self.valueLabel.setGeometry(QtCore.QRect(10, 40, 41, 16))
        self.valueLabel.setObjectName("valueLabel")
        self.loadLabel = QtWidgets.QLabel(parent=SourceWidget)
        self.loadLabel.setGeometry(QtCore.QRect(10, 70, 41, 16))
        self.loadLabel.setObjectName("loadLabel")
        self.loadValueLabel = QtWidgets.QLabel(parent=SourceWidget)
        self.loadValueLabel.setGeometry(QtCore.QRect(60, 70, 111, 16))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.loadValueLabel.setFont(font)
        self.loadValueLabel.setText("")
        self.loadValueLabel.setObjectName("loadValueLabel")
        self.nodeTypeLabel = QtWidgets.QLabel(parent=SourceWidget)
        self.nodeTypeLabel.setGeometry(QtCore.QRect(10, 10, 161, 20))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.nodeTypeLabel.setFont(font)
        self.nodeTypeLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.nodeTypeLabel.setObjectName("nodeTypeLabel")

        self.retranslateUi(SourceWidget)
        QtCore.QMetaObject.connectSlotsByName(SourceWidget)

    def retranslateUi(self, SourceWidget):
        _translate = QtCore.QCoreApplication.translate
        SourceWidget.setWindowTitle(_translate("SourceWidget", "Form"))
        self.valueLabel.setText(_translate("SourceWidget", "Voltage:"))
        self.loadLabel.setText(_translate("SourceWidget", "Load:"))
        self.nodeTypeLabel.setText(_translate("SourceWidget", "Power Input"))
