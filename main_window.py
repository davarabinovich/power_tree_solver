# Form implementation generated from reading ui file 'main_window.ui'
#
# Created by: PyQt6 UI code generator 6.5.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1250, 821)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)
        self.centralwidget.setObjectName("centralwidget")
        self.graphview = NetView(parent=self.centralwidget)
        self.graphview.setGeometry(QtCore.QRect(0, -22, 1250, 800))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.graphview.sizePolicy().hasHeightForWidth())
        self.graphview.setSizePolicy(sizePolicy)
        self.graphview.setObjectName("graphview")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(parent=MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1250, 22))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(parent=self.menubar)
        self.menuFile.setObjectName("menuFile")
        MainWindow.setMenuBar(self.menubar)
        self.statusBar = QtWidgets.QStatusBar(parent=MainWindow)
        self.statusBar.setObjectName("statusBar")
        MainWindow.setStatusBar(self.statusBar)
        self.actionSaveAs = QtGui.QAction(parent=MainWindow)
        self.actionSaveAs.setEnabled(False)
        self.actionSaveAs.setObjectName("actionSaveAs")
        self.actionLoadFrom = QtGui.QAction(parent=MainWindow)
        self.actionLoadFrom.setObjectName("actionLoadFrom")
        self.actionCreateNew = QtGui.QAction(parent=MainWindow)
        self.actionCreateNew.setObjectName("actionCreateNew")
        self.menuFile.addAction(self.actionCreateNew)
        self.menuFile.addAction(self.actionLoadFrom)
        self.menuFile.addAction(self.actionSaveAs)
        self.menubar.addAction(self.menuFile.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Power Tree Solver 0.1 alfa"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.actionSaveAs.setText(_translate("MainWindow", "Save As..."))
        self.actionLoadFrom.setText(_translate("MainWindow", "Load From..."))
        self.actionCreateNew.setText(_translate("MainWindow", "Create New"))
from net_view import NetView
