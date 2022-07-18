# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'MainWindow.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from ViewerEditorImage import ViewerEditorImage
from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName('MainWindow')
        MainWindow.resize(1591, 828)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)
        self.centralwidget.setObjectName('centralwidget')
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName('gridLayout')
        self.splitter_4 = QtWidgets.QSplitter(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.splitter_4.sizePolicy().hasHeightForWidth())
        self.splitter_4.setSizePolicy(sizePolicy)
        self.splitter_4.setOrientation(QtCore.Qt.Horizontal)
        self.splitter_4.setObjectName('splitter_4')
        self.verticalLayoutWidget = QtWidgets.QWidget(self.splitter_4)
        self.verticalLayoutWidget.setObjectName('verticalLayoutWidget')
        self.verticalLayoutLeft = QtWidgets.QVBoxLayout(
            self.verticalLayoutWidget)
        self.verticalLayoutLeft.setSizeConstraint(
            QtWidgets.QLayout.SetMaximumSize)
        self.verticalLayoutLeft.setContentsMargins(0, 0, 0, 0)
        self.verticalLayoutLeft.setObjectName('verticalLayoutLeft')
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName('horizontalLayout')
        self.isSavedCheckBox = QtWidgets.QCheckBox(self.verticalLayoutWidget)
        self.isSavedCheckBox.setObjectName('isSavedCheckBox')
        self.horizontalLayout.addWidget(self.isSavedCheckBox)
        self.progressBar = QtWidgets.QProgressBar(self.verticalLayoutWidget)
        self.progressBar.setProperty('value', 24)
        self.progressBar.setObjectName('progressBar')
        self.horizontalLayout.addWidget(self.progressBar)
        self.verticalLayoutLeft.addLayout(self.horizontalLayout)
        self.viewerEditor = ViewerEditorImage(self.verticalLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.viewerEditor.sizePolicy().hasHeightForWidth())
        self.viewerEditor.setSizePolicy(sizePolicy)
        self.viewerEditor.setMinimumSize(QtCore.QSize(800, 240))
        self.viewerEditor.setObjectName('viewerEditor')
        self.verticalLayoutLeft.addWidget(self.viewerEditor)
        self.layoutWidget = QtWidgets.QWidget(self.splitter_4)
        self.layoutWidget.setObjectName('layoutWidget')
        self.verticalLayoutRight = QtWidgets.QVBoxLayout(self.layoutWidget)
        self.verticalLayoutRight.setSizeConstraint(
            QtWidgets.QLayout.SetMaximumSize)
        self.verticalLayoutRight.setContentsMargins(0, 0, 0, 0)
        self.verticalLayoutRight.setObjectName('verticalLayoutRight')
        self.fileLabel = QtWidgets.QLabel(self.layoutWidget)
        self.fileLabel.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.fileLabel.sizePolicy().hasHeightForWidth())
        self.fileLabel.setSizePolicy(sizePolicy)
        self.fileLabel.setMinimumSize(QtCore.QSize(300, 32))
        self.fileLabel.setObjectName('fileLabel')
        self.verticalLayoutRight.addWidget(self.fileLabel)
        self.sliderLayout = QtWidgets.QHBoxLayout()
        self.sliderLayout.setObjectName('sliderLayout')
        self.fileNumberSliderLabel = QtWidgets.QLabel(self.layoutWidget)
        self.fileNumberSliderLabel.setObjectName('fileNumberSliderLabel')
        self.sliderLayout.addWidget(self.fileNumberSliderLabel)
        self.fileNumberSlider = QtWidgets.QSlider(self.layoutWidget)
        self.fileNumberSlider.setOrientation(QtCore.Qt.Horizontal)
        self.fileNumberSlider.setTickPosition(QtWidgets.QSlider.TicksAbove)
        self.fileNumberSlider.setObjectName('fileNumberSlider')
        self.sliderLayout.addWidget(self.fileNumberSlider)
        self.verticalLayoutRight.addLayout(self.sliderLayout)
        self.fileSelectorTableWidget = QtWidgets.QTableWidget(
            self.layoutWidget)
        self.fileSelectorTableWidget.setObjectName('fileSelectorTableWidget')
        self.fileSelectorTableWidget.setColumnCount(0)
        self.fileSelectorTableWidget.setRowCount(0)
        self.verticalLayoutRight.addWidget(self.fileSelectorTableWidget)
        self.detectorClassesLabel = QtWidgets.QLabel(self.layoutWidget)
        self.detectorClassesLabel.setObjectName('detectorClassesLabel')
        self.verticalLayoutRight.addWidget(self.detectorClassesLabel)
        self.labelsListWidget = QtWidgets.QListWidget(self.layoutWidget)
        self.labelsListWidget.setObjectName('labelsListWidget')
        self.verticalLayoutRight.addWidget(self.labelsListWidget)
        spacerItem = QtWidgets.QSpacerItem(
            20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayoutRight.addItem(spacerItem)
        self.gridLayout.addWidget(self.splitter_4, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1591, 22))
        self.menubar.setObjectName('menubar')
        self.menuMenu = QtWidgets.QMenu(self.menubar)
        self.menuMenu.setObjectName('menuMenu')
        self.menuPomoc = QtWidgets.QMenu(self.menubar)
        self.menuPomoc.setObjectName('menuPomoc')
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName('statusbar')
        MainWindow.setStatusBar(self.statusbar)
        self.actionOtw_rz = QtWidgets.QAction(MainWindow)
        self.actionOtw_rz.setObjectName('actionOtw_rz')
        self.actionZamknij = QtWidgets.QAction(MainWindow)
        self.actionZamknij.setObjectName('actionZamknij')
        self.actionO_programie = QtWidgets.QAction(MainWindow)
        self.actionO_programie.setObjectName('actionO_programie')
        self.actionOtworzLokacje = QtWidgets.QAction(MainWindow)
        self.actionOtworzLokacje.setObjectName('actionOtworzLokacje')
        self.actionZamknijProgram = QtWidgets.QAction(MainWindow)
        self.actionZamknijProgram.setObjectName('actionZamknijProgram')
        self.actionZapisz = QtWidgets.QAction(MainWindow)
        self.actionZapisz.setObjectName('actionZapisz')
        self.actionNextLocation = QtWidgets.QAction(MainWindow)
        self.actionNextLocation.setObjectName('actionNextLocation')
        self.actionPrevLocation = QtWidgets.QAction(MainWindow)
        self.actionPrevLocation.setObjectName('actionPrevLocation')
        self.actionMountRO = QtWidgets.QAction(MainWindow)
        self.actionMountRO.setObjectName('actionMountRO')
        self.actionNextConfiguration = QtWidgets.QAction(MainWindow)
        self.actionNextConfiguration.setObjectName('actionNextConfiguration')
        self.actionPrevConfiguration = QtWidgets.QAction(MainWindow)
        self.actionPrevConfiguration.setObjectName('actionPrevConfiguration')
        self.menuMenu.addAction(self.actionOtworzLokacje)
        self.menuMenu.addAction(self.actionZapisz)
        self.menuMenu.addAction(self.actionZamknijProgram)
        self.menubar.addAction(self.menuMenu.menuAction())
        self.menubar.addAction(self.menuPomoc.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate(
            'MainWindow', 'AITracker - config'))
        self.isSavedCheckBox.setText(_translate('MainWindow', 'Saved'))
        self.fileLabel.setText(_translate(
            'MainWindow', 'Filename (number/all)'))
        self.fileNumberSliderLabel.setText(
            _translate('MainWindow', 'Slider label'))
        self.detectorClassesLabel.setText(_translate(
            'MainWindow', 'Selected detector classes :'))
        self.menuMenu.setTitle(_translate('MainWindow', 'Menu'))
        self.menuPomoc.setTitle(_translate('MainWindow', 'Help'))
        self.actionOtw_rz.setText(_translate('MainWindow', 'Otwórz'))
        self.actionZamknij.setText(_translate('MainWindow', 'Zamknij'))
        self.actionO_programie.setText(_translate('MainWindow', 'O programie'))
        self.actionOtworzLokacje.setText(
            _translate('MainWindow', 'Open directory'))
        self.actionOtworzLokacje.setShortcut(
            _translate('MainWindow', 'Ctrl+O'))
        self.actionZamknijProgram.setText(_translate('MainWindow', 'Exit'))
        self.actionZamknijProgram.setShortcut(
            _translate('MainWindow', 'Ctrl+X'))
        self.actionZapisz.setText(_translate('MainWindow', 'Save'))
        self.actionZapisz.setShortcut(_translate('MainWindow', 'Ctrl+S', 'S'))
        self.actionNextLocation.setText(
            _translate('MainWindow', 'Następna lokacja'))
        self.actionNextLocation.setShortcut(_translate('MainWindow', 'Ctrl+N'))
        self.actionPrevLocation.setText(
            _translate('MainWindow', 'Poprzednia lokacja'))
        self.actionPrevLocation.setShortcut(_translate('MainWindow', 'Ctrl+B'))
        self.actionMountRO.setText(_translate(
            'MainWindow', 'Przemontuj lokacje'))
        self.actionNextConfiguration.setText(
            _translate('MainWindow', 'Następna konfiguracja'))
        self.actionNextConfiguration.setShortcut(
            _translate('MainWindow', 'Ctrl+.'))
        self.actionPrevConfiguration.setText(
            _translate('MainWindow', 'Poprzednia konfiguracja'))
        self.actionPrevConfiguration.setShortcut(
            _translate('MainWindow', 'Ctrl+,'))
