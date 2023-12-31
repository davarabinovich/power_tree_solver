# Form implementation generated from reading ui file 'converter_node.ui'
#
# Created by: PyQt6 UI code generator 6.5.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_ConverterWidget(object):
    def setupUi(self, ConverterWidget):
        ConverterWidget.setObjectName("ConverterWidget")
        ConverterWidget.resize(170, 125)
        self.valueLineEdit = QtWidgets.QLineEdit(parent=ConverterWidget)
        self.valueLineEdit.setGeometry(QtCore.QRect(50, 50, 115, 20))
        self.valueLineEdit.setObjectName("valueLineEdit")
        self.valueLabel = QtWidgets.QLabel(parent=ConverterWidget)
        self.valueLabel.setGeometry(QtCore.QRect(5, 50, 40, 20))
        self.valueLabel.setObjectName("valueLabel")
        self.loadLabel = QtWidgets.QLabel(parent=ConverterWidget)
        self.loadLabel.setGeometry(QtCore.QRect(5, 75, 40, 20))
        self.loadLabel.setObjectName("loadLabel")
        self.loadValueLabel = QtWidgets.QLabel(parent=ConverterWidget)
        self.loadValueLabel.setGeometry(QtCore.QRect(50, 75, 115, 20))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.loadValueLabel.setFont(font)
        self.loadValueLabel.setText("")
        self.loadValueLabel.setObjectName("loadValueLabel")
        self.linearRadioButton = QtWidgets.QRadioButton(parent=ConverterWidget)
        self.linearRadioButton.setGeometry(QtCore.QRect(10, 100, 75, 15))
        self.linearRadioButton.setObjectName("linearRadioButton")
        self.typeButtonGroup = QtWidgets.QButtonGroup(ConverterWidget)
        self.typeButtonGroup.setObjectName("typeButtonGroup")
        self.typeButtonGroup.addButton(self.linearRadioButton)
        self.switchingRadioButton = QtWidgets.QRadioButton(parent=ConverterWidget)
        self.switchingRadioButton.setGeometry(QtCore.QRect(90, 100, 75, 15))
        self.switchingRadioButton.setChecked(True)
        self.switchingRadioButton.setObjectName("switchingRadioButton")
        self.typeButtonGroup.addButton(self.switchingRadioButton)
        self.nodeTypeLabel = QtWidgets.QLabel(parent=ConverterWidget)
        self.nodeTypeLabel.setGeometry(QtCore.QRect(5, 5, 160, 15))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.nodeTypeLabel.setFont(font)
        self.nodeTypeLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.nodeTypeLabel.setObjectName("nodeTypeLabel")
        self.nameLineEdit = QtWidgets.QLineEdit(parent=ConverterWidget)
        self.nameLineEdit.setGeometry(QtCore.QRect(50, 25, 115, 20))
        self.nameLineEdit.setObjectName("nameLineEdit")
        self.nameLabel = QtWidgets.QLabel(parent=ConverterWidget)
        self.nameLabel.setGeometry(QtCore.QRect(5, 25, 40, 20))
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(False)
        font.setWeight(50)
        self.nameLabel.setFont(font)
        self.nameLabel.setObjectName("nameLabel")

        self.retranslateUi(ConverterWidget)
        QtCore.QMetaObject.connectSlotsByName(ConverterWidget)

    def retranslateUi(self, ConverterWidget):
        _translate = QtCore.QCoreApplication.translate
        ConverterWidget.setWindowTitle(_translate("ConverterWidget", "Form"))
        self.valueLabel.setText(_translate("ConverterWidget", "Voltage:"))
        self.loadLabel.setText(_translate("ConverterWidget", "Load:"))
        self.linearRadioButton.setText(_translate("ConverterWidget", "Linear"))
        self.switchingRadioButton.setText(_translate("ConverterWidget", "Switching"))
        self.nodeTypeLabel.setText(_translate("ConverterWidget", "Converter"))
        self.nameLabel.setText(_translate("ConverterWidget", "Name:"))
