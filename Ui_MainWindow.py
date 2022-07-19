# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'MainWindow.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from ViewerEditorImage import ViewerEditorImage
import tango_rc
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
        self.isSavedCheckBox.setCheckable(False)
        self.isSavedCheckBox.setObjectName('isSavedCheckBox')
        self.horizontalLayout.addWidget(self.isSavedCheckBox)
        self.progressBar = QtWidgets.QProgressBar(self.verticalLayoutWidget)
        self.progressBar.setProperty('value', 0)
        self.progressBar.setTextVisible(True)
        self.progressBar.setTextDirection(QtWidgets.QProgressBar.TopToBottom)
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
        self.prevFileButton = QtWidgets.QToolButton(self.layoutWidget)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(
            ':/icons/16x16/media-skip-backward.png'), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.prevFileButton.setIcon(icon)
        self.prevFileButton.setObjectName('prevFileButton')
        self.sliderLayout.addWidget(self.prevFileButton)
        self.fileNumberSlider = QtWidgets.QSlider(self.layoutWidget)
        self.fileNumberSlider.setOrientation(QtCore.Qt.Horizontal)
        self.fileNumberSlider.setTickPosition(QtWidgets.QSlider.TicksAbove)
        self.fileNumberSlider.setObjectName('fileNumberSlider')
        self.sliderLayout.addWidget(self.fileNumberSlider)
        self.nextFileButton = QtWidgets.QToolButton(self.layoutWidget)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(
            ':/icons/16x16/media-skip-forward.png'), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.nextFileButton.setIcon(icon1)
        self.nextFileButton.setObjectName('nextFileButton')
        self.sliderLayout.addWidget(self.nextFileButton)
        self.verticalLayoutRight.addLayout(self.sliderLayout)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName('horizontalLayout_2')
        self.label_2 = QtWidgets.QLabel(self.layoutWidget)
        self.label_2.setObjectName('label_2')
        self.horizontalLayout_2.addWidget(self.label_2)
        self.SaveFileAnnotationsButton = QtWidgets.QPushButton(
            self.layoutWidget)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(
            ':/icons/16x16/document-save-as.png'), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.SaveFileAnnotationsButton.setIcon(icon2)
        self.SaveFileAnnotationsButton.setObjectName(
            'SaveFileAnnotationsButton')
        self.horizontalLayout_2.addWidget(self.SaveFileAnnotationsButton)
        self.DeleteImageAnnotationsButton = QtWidgets.QPushButton(
            self.layoutWidget)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(
            ':/icons/16x16/process-stop.png'), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.DeleteImageAnnotationsButton.setIcon(icon3)
        self.DeleteImageAnnotationsButton.setObjectName(
            'DeleteImageAnnotationsButton')
        self.horizontalLayout_2.addWidget(self.DeleteImageAnnotationsButton)
        spacerItem = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.verticalLayoutRight.addLayout(self.horizontalLayout_2)
        self.fileSelectorTableWidget = QtWidgets.QTableWidget(
            self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.fileSelectorTableWidget.sizePolicy().hasHeightForWidth())
        self.fileSelectorTableWidget.setSizePolicy(sizePolicy)
        self.fileSelectorTableWidget.setObjectName('fileSelectorTableWidget')
        self.fileSelectorTableWidget.setColumnCount(0)
        self.fileSelectorTableWidget.setRowCount(0)
        self.verticalLayoutRight.addWidget(self.fileSelectorTableWidget)
        self.line = QtWidgets.QFrame(self.layoutWidget)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName('line')
        self.verticalLayoutRight.addWidget(self.line)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName('horizontalLayout_3')
        self.label = QtWidgets.QLabel(self.layoutWidget)
        self.label.setMinimumSize(QtCore.QSize(90, 0))
        self.label.setObjectName('label')
        self.horizontalLayout_3.addWidget(self.label)
        self.addAnnotationsButton = QtWidgets.QPushButton(self.layoutWidget)
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(':/icons/16x16/list-add.png'),
                        QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.addAnnotationsButton.setIcon(icon4)
        self.addAnnotationsButton.setCheckable(True)
        self.addAnnotationsButton.setFlat(False)
        self.addAnnotationsButton.setObjectName('addAnnotationsButton')
        self.horizontalLayout_3.addWidget(self.addAnnotationsButton)
        self.removeAnnotationsButton = QtWidgets.QPushButton(self.layoutWidget)
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap(':/icons/16x16/list-remove.png'),
                        QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.removeAnnotationsButton.setIcon(icon5)
        self.removeAnnotationsButton.setCheckable(True)
        self.removeAnnotationsButton.setObjectName('removeAnnotationsButton')
        self.horizontalLayout_3.addWidget(self.removeAnnotationsButton)
        self.ClearAnnotationsButton = QtWidgets.QPushButton(self.layoutWidget)
        icon6 = QtGui.QIcon()
        icon6.addPixmap(QtGui.QPixmap(':/icons/16x16/edit-clear.png'),
                        QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.ClearAnnotationsButton.setIcon(icon6)
        self.ClearAnnotationsButton.setObjectName('ClearAnnotationsButton')
        self.horizontalLayout_3.addWidget(self.ClearAnnotationsButton)
        self.hideAnnotationsButton = QtWidgets.QPushButton(self.layoutWidget)
        icon7 = QtGui.QIcon()
        icon7.addPixmap(QtGui.QPixmap(':/icons/16x16/go-jump.png'),
                        QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.hideAnnotationsButton.setIcon(icon7)
        self.hideAnnotationsButton.setObjectName('hideAnnotationsButton')
        self.horizontalLayout_3.addWidget(self.hideAnnotationsButton)
        self.detectAnnotationsButton = QtWidgets.QPushButton(self.layoutWidget)
        icon8 = QtGui.QIcon()
        icon8.addPixmap(QtGui.QPixmap(
            ':/icons/16x16/camera-photo.png'), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.detectAnnotationsButton.setIcon(icon8)
        self.detectAnnotationsButton.setObjectName('detectAnnotationsButton')
        self.horizontalLayout_3.addWidget(self.detectAnnotationsButton)
        spacerItem1 = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem1)
        self.verticalLayoutRight.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName('horizontalLayout_4')
        self.label_3 = QtWidgets.QLabel(self.layoutWidget)
        self.label_3.setMinimumSize(QtCore.QSize(90, 0))
        self.label_3.setObjectName('label_3')
        self.horizontalLayout_4.addWidget(self.label_3)
        self.paintCircleButton = QtWidgets.QPushButton(self.layoutWidget)
        icon9 = QtGui.QIcon()
        icon9.addPixmap(QtGui.QPixmap(':/icons/32x32/list-add.png'),
                        QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.paintCircleButton.setIcon(icon9)
        self.paintCircleButton.setCheckable(True)
        self.paintCircleButton.setObjectName('paintCircleButton')
        self.horizontalLayout_4.addWidget(self.paintCircleButton)
        spacerItem2 = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem2)
        self.verticalLayoutRight.addLayout(self.horizontalLayout_4)
        self.toolSettingsStackedWidget = QtWidgets.QStackedWidget(
            self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.toolSettingsStackedWidget.sizePolicy().hasHeightForWidth())
        self.toolSettingsStackedWidget.setSizePolicy(sizePolicy)
        self.toolSettingsStackedWidget.setFrameShape(
            QtWidgets.QFrame.StyledPanel)
        self.toolSettingsStackedWidget.setFrameShadow(QtWidgets.QFrame.Plain)
        self.toolSettingsStackedWidget.setLineWidth(1)
        self.toolSettingsStackedWidget.setObjectName(
            'toolSettingsStackedWidget')
        self.pageAnnotations = QtWidgets.QWidget()
        self.pageAnnotations.setObjectName('pageAnnotations')
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.pageAnnotations)
        self.verticalLayout_2.setObjectName('verticalLayout_2')
        self.detectorClassesLabel = QtWidgets.QLabel(self.pageAnnotations)
        self.detectorClassesLabel.setObjectName('detectorClassesLabel')
        self.verticalLayout_2.addWidget(self.detectorClassesLabel)
        self.labelsListWidget = QtWidgets.QListWidget(self.pageAnnotations)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.labelsListWidget.sizePolicy().hasHeightForWidth())
        self.labelsListWidget.setSizePolicy(sizePolicy)
        self.labelsListWidget.setDefaultDropAction(QtCore.Qt.IgnoreAction)
        self.labelsListWidget.setSelectionMode(
            QtWidgets.QAbstractItemView.SingleSelection)
        self.labelsListWidget.setSelectionBehavior(
            QtWidgets.QAbstractItemView.SelectItems)
        self.labelsListWidget.setObjectName('labelsListWidget')
        self.verticalLayout_2.addWidget(self.labelsListWidget)
        spacerItem3 = QtWidgets.QSpacerItem(
            20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem3)
        self.toolSettingsStackedWidget.addWidget(self.pageAnnotations)
        self.pageCircle = QtWidgets.QWidget()
        self.pageCircle.setObjectName('pageCircle')
        self.verticalLayout = QtWidgets.QVBoxLayout(self.pageCircle)
        self.verticalLayout.setObjectName('verticalLayout')
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName('horizontalLayout_5')
        self.paintLabel = QtWidgets.QLabel(self.pageCircle)
        self.paintLabel.setObjectName('paintLabel')
        self.horizontalLayout_5.addWidget(self.paintLabel)
        self.paintSizeSlider = QtWidgets.QSlider(self.pageCircle)
        self.paintSizeSlider.setMinimum(5)
        self.paintSizeSlider.setMaximum(55)
        self.paintSizeSlider.setSingleStep(10)
        self.paintSizeSlider.setOrientation(QtCore.Qt.Horizontal)
        self.paintSizeSlider.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.paintSizeSlider.setObjectName('paintSizeSlider')
        self.horizontalLayout_5.addWidget(self.paintSizeSlider)
        self.verticalLayout.addLayout(self.horizontalLayout_5)
        spacerItem4 = QtWidgets.QSpacerItem(
            20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem4)
        self.toolSettingsStackedWidget.addWidget(self.pageCircle)
        self.verticalLayoutRight.addWidget(self.toolSettingsStackedWidget)
        self.gridLayout.addWidget(self.splitter_4, 1, 0, 1, 1)
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
        self.toolSettingsStackedWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate(
            'MainWindow', 'AITracker - config'))
        self.isSavedCheckBox.setText(_translate('MainWindow', 'Saved'))
        self.progressBar.setFormat(_translate('MainWindow', 'Annotated %p%'))
        self.fileLabel.setText(_translate(
            'MainWindow', 'Filename (number/all)'))
        self.fileNumberSliderLabel.setText(
            _translate('MainWindow', 'Slider label'))
        self.prevFileButton.setText(_translate('MainWindow', '...'))
        self.prevFileButton.setShortcut(_translate('MainWindow', ','))
        self.nextFileButton.setText(_translate('MainWindow', '...'))
        self.nextFileButton.setShortcut(_translate('MainWindow', '.'))
        self.label_2.setText(_translate('MainWindow', 'Image'))
        self.SaveFileAnnotationsButton.setText(
            _translate('MainWindow', 'Save'))
        self.SaveFileAnnotationsButton.setShortcut(
            _translate('MainWindow', 'S'))
        self.DeleteImageAnnotationsButton.setText(
            _translate('MainWindow', 'Delete'))
        self.DeleteImageAnnotationsButton.setShortcut(
            _translate('MainWindow', 'X'))
        self.label.setText(_translate('MainWindow', 'Annotations'))
        self.addAnnotationsButton.setText(_translate('MainWindow', 'Add '))
        self.addAnnotationsButton.setShortcut(_translate('MainWindow', 'A'))
        self.removeAnnotationsButton.setText(
            _translate('MainWindow', 'Remove'))
        self.removeAnnotationsButton.setShortcut(_translate('MainWindow', 'R'))
        self.ClearAnnotationsButton.setText(_translate('MainWindow', 'Clear'))
        self.ClearAnnotationsButton.setShortcut(_translate('MainWindow', 'C'))
        self.hideAnnotationsButton.setText(_translate('MainWindow', 'Hide'))
        self.hideAnnotationsButton.setShortcut(_translate('MainWindow', 'H'))
        self.detectAnnotationsButton.setText(
            _translate('MainWindow', 'Detect '))
        self.detectAnnotationsButton.setShortcut(_translate('MainWindow', 'D'))
        self.label_3.setText(_translate('MainWindow', 'Painting'))
        self.paintCircleButton.setText(_translate('MainWindow', 'Add Circle'))
        self.detectorClassesLabel.setText(_translate(
            'MainWindow', 'Selected detector classes :'))
        self.paintLabel.setText(_translate('MainWindow', 'Painting Size'))
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
