# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'MainWindow.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets
from ViewerEditorImage import ViewerEditorImage
import tango_rc


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
        self.isErrorsCheckBox = QtWidgets.QCheckBox(self.verticalLayoutWidget)
        self.isErrorsCheckBox.setCheckable(False)
        self.isErrorsCheckBox.setObjectName('isErrorsCheckBox')
        self.horizontalLayout.addWidget(self.isErrorsCheckBox)
        self.label_4 = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.label_4.setObjectName('label_4')
        self.horizontalLayout.addWidget(self.label_4)
        self.imageScalingComboBox = QtWidgets.QComboBox(
            self.verticalLayoutWidget)
        self.imageScalingComboBox.setObjectName('imageScalingComboBox')
        self.imageScalingComboBox.addItem('')
        self.imageScalingComboBox.addItem('')
        self.imageScalingComboBox.addItem('')
        self.horizontalLayout.addWidget(self.imageScalingComboBox)
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
        self.viewerEditor.setMinimumSize(QtCore.QSize(100, 100))
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
        self.nextFileButton = QtWidgets.QToolButton(self.layoutWidget)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(
            ':/icons/16x16/media-skip-forward.png'), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.nextFileButton.setIcon(icon1)
        self.nextFileButton.setObjectName('nextFileButton')
        self.sliderLayout.addWidget(self.nextFileButton)
        spacerItem = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.sliderLayout.addItem(spacerItem)
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
        self.DeleteNotAnnotatedFilesButton = QtWidgets.QPushButton(
            self.layoutWidget)
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(
            ':/icons/32x32/process-stop.png'), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.DeleteNotAnnotatedFilesButton.setIcon(icon4)
        self.DeleteNotAnnotatedFilesButton.setObjectName(
            'DeleteNotAnnotatedFilesButton')
        self.horizontalLayout_2.addWidget(self.DeleteNotAnnotatedFilesButton)
        spacerItem1 = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.verticalLayoutRight.addLayout(self.horizontalLayout_2)
        self.fileSummaryLabel = QtWidgets.QLabel(self.layoutWidget)
        self.fileSummaryLabel.setTextFormat(QtCore.Qt.MarkdownText)
        self.fileSummaryLabel.setObjectName('fileSummaryLabel')
        self.verticalLayoutRight.addWidget(self.fileSummaryLabel)
        self.fileSelectorTableWidget = QtWidgets.QTableWidget(
            self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.fileSelectorTableWidget.sizePolicy().hasHeightForWidth())
        self.fileSelectorTableWidget.setSizePolicy(sizePolicy)
        self.fileSelectorTableWidget.setMinimumSize(QtCore.QSize(0, 200))
        self.fileSelectorTableWidget.setVerticalScrollBarPolicy(
            QtCore.Qt.ScrollBarAlwaysOn)
        self.fileSelectorTableWidget.setSizeAdjustPolicy(
            QtWidgets.QAbstractScrollArea.AdjustToContentsOnFirstShow)
        self.fileSelectorTableWidget.setSelectionMode(
            QtWidgets.QAbstractItemView.SingleSelection)
        self.fileSelectorTableWidget.setSelectionBehavior(
            QtWidgets.QAbstractItemView.SelectRows)
        self.fileSelectorTableWidget.setObjectName('fileSelectorTableWidget')
        self.fileSelectorTableWidget.setColumnCount(0)
        self.fileSelectorTableWidget.setRowCount(0)
        self.verticalLayoutRight.addWidget(self.fileSelectorTableWidget)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName('horizontalLayout_3')
        self.label = QtWidgets.QLabel(self.layoutWidget)
        self.label.setMinimumSize(QtCore.QSize(90, 0))
        self.label.setObjectName('label')
        self.horizontalLayout_3.addWidget(self.label)
        self.addAnnotationsButton = QtWidgets.QPushButton(self.layoutWidget)
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap(':/icons/16x16/list-add.png'),
                        QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.addAnnotationsButton.setIcon(icon5)
        self.addAnnotationsButton.setCheckable(True)
        self.addAnnotationsButton.setFlat(False)
        self.addAnnotationsButton.setObjectName('addAnnotationsButton')
        self.horizontalLayout_3.addWidget(self.addAnnotationsButton)
        self.renameAnnotationsButton = QtWidgets.QPushButton(self.layoutWidget)
        icon6 = QtGui.QIcon()
        icon6.addPixmap(QtGui.QPixmap(
            ':/icons/32x32/accessories-text-editor.png'), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.renameAnnotationsButton.setIcon(icon6)
        self.renameAnnotationsButton.setCheckable(True)
        self.renameAnnotationsButton.setObjectName('renameAnnotationsButton')
        self.horizontalLayout_3.addWidget(self.renameAnnotationsButton)
        self.removeAnnotationsButton = QtWidgets.QPushButton(self.layoutWidget)
        icon7 = QtGui.QIcon()
        icon7.addPixmap(QtGui.QPixmap(':/icons/16x16/list-remove.png'),
                        QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.removeAnnotationsButton.setIcon(icon7)
        self.removeAnnotationsButton.setCheckable(True)
        self.removeAnnotationsButton.setObjectName('removeAnnotationsButton')
        self.horizontalLayout_3.addWidget(self.removeAnnotationsButton)
        self.ClearAnnotationsButton = QtWidgets.QPushButton(self.layoutWidget)
        icon8 = QtGui.QIcon()
        icon8.addPixmap(QtGui.QPixmap(':/icons/16x16/edit-clear.png'),
                        QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.ClearAnnotationsButton.setIcon(icon8)
        self.ClearAnnotationsButton.setObjectName('ClearAnnotationsButton')
        self.horizontalLayout_3.addWidget(self.ClearAnnotationsButton)
        self.hideLabelsButton = QtWidgets.QPushButton(self.layoutWidget)
        icon9 = QtGui.QIcon()
        icon9.addPixmap(QtGui.QPixmap(':/icons/32x32/go-jump.png'),
                        QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.hideLabelsButton.setIcon(icon9)
        self.hideLabelsButton.setObjectName('hideLabelsButton')
        self.horizontalLayout_3.addWidget(self.hideLabelsButton)
        self.hideAnnotationsButton = QtWidgets.QPushButton(self.layoutWidget)
        icon10 = QtGui.QIcon()
        icon10.addPixmap(QtGui.QPixmap(':/icons/16x16/go-jump.png'),
                         QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.hideAnnotationsButton.setIcon(icon10)
        self.hideAnnotationsButton.setObjectName('hideAnnotationsButton')
        self.horizontalLayout_3.addWidget(self.hideAnnotationsButton)
        self.detectAnnotationsButton = QtWidgets.QPushButton(self.layoutWidget)
        icon11 = QtGui.QIcon()
        icon11.addPixmap(QtGui.QPixmap(
            ':/icons/16x16/camera-photo.png'), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.detectAnnotationsButton.setIcon(icon11)
        self.detectAnnotationsButton.setObjectName('detectAnnotationsButton')
        self.horizontalLayout_3.addWidget(self.detectAnnotationsButton)
        spacerItem2 = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem2)
        self.verticalLayoutRight.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName('horizontalLayout_4')
        self.label_3 = QtWidgets.QLabel(self.layoutWidget)
        self.label_3.setMinimumSize(QtCore.QSize(90, 0))
        self.label_3.setObjectName('label_3')
        self.horizontalLayout_4.addWidget(self.label_3)
        self.paintCircleButton = QtWidgets.QPushButton(self.layoutWidget)
        icon12 = QtGui.QIcon()
        icon12.addPixmap(QtGui.QPixmap(':/icons/32x32/list-add.png'),
                         QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.paintCircleButton.setIcon(icon12)
        self.paintCircleButton.setCheckable(True)
        self.paintCircleButton.setObjectName('paintCircleButton')
        self.horizontalLayout_4.addWidget(self.paintCircleButton)
        spacerItem3 = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem3)
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
        self.labelsListWidget.setMinimumSize(QtCore.QSize(0, 250))
        self.labelsListWidget.setDefaultDropAction(QtCore.Qt.IgnoreAction)
        self.labelsListWidget.setSelectionMode(
            QtWidgets.QAbstractItemView.SingleSelection)
        self.labelsListWidget.setSelectionBehavior(
            QtWidgets.QAbstractItemView.SelectItems)
        self.labelsListWidget.setObjectName('labelsListWidget')
        self.verticalLayout_2.addWidget(self.labelsListWidget)
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_6.setObjectName('horizontalLayout_6')
        self.frame = QtWidgets.QFrame(self.pageAnnotations)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName('frame')
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout(self.frame)
        self.horizontalLayout_7.setObjectName('horizontalLayout_7')
        self.button2 = QtWidgets.QPushButton(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.button2.sizePolicy().hasHeightForWidth())
        self.button2.setSizePolicy(sizePolicy)
        self.button2.setMaximumSize(QtCore.QSize(20, 16777215))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.button2.setFont(font)
        self.button2.setFlat(True)
        self.button2.setObjectName('button2')
        self.horizontalLayout_7.addWidget(self.button2)
        self.button5 = QtWidgets.QPushButton(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.button5.sizePolicy().hasHeightForWidth())
        self.button5.setSizePolicy(sizePolicy)
        self.button5.setMaximumSize(QtCore.QSize(20, 16777215))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.button5.setFont(font)
        self.button5.setFlat(True)
        self.button5.setObjectName('button5')
        self.horizontalLayout_7.addWidget(self.button5)
        self.button7 = QtWidgets.QPushButton(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.button7.sizePolicy().hasHeightForWidth())
        self.button7.setSizePolicy(sizePolicy)
        self.button7.setMaximumSize(QtCore.QSize(20, 16777215))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.button7.setFont(font)
        self.button7.setFlat(True)
        self.button7.setObjectName('button7')
        self.horizontalLayout_7.addWidget(self.button7)
        self.button8 = QtWidgets.QPushButton(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.button8.sizePolicy().hasHeightForWidth())
        self.button8.setSizePolicy(sizePolicy)
        self.button8.setMaximumSize(QtCore.QSize(20, 16777215))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.button8.setFont(font)
        self.button8.setFlat(True)
        self.button8.setObjectName('button8')
        self.horizontalLayout_7.addWidget(self.button8)
        self.button1 = QtWidgets.QPushButton(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.button1.sizePolicy().hasHeightForWidth())
        self.button1.setSizePolicy(sizePolicy)
        self.button1.setMaximumSize(QtCore.QSize(20, 16777215))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.button1.setFont(font)
        self.button1.setDefault(False)
        self.button1.setFlat(True)
        self.button1.setObjectName('button1')
        self.horizontalLayout_7.addWidget(self.button1)
        self.buttonOffset = QtWidgets.QPushButton(self.frame)
        self.buttonOffset.setMaximumSize(QtCore.QSize(22, 16777215))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.buttonOffset.setFont(font)
        self.buttonOffset.setFlat(True)
        self.buttonOffset.setObjectName('buttonOffset')
        self.horizontalLayout_7.addWidget(self.buttonOffset)
        self.button9 = QtWidgets.QPushButton(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.button9.sizePolicy().hasHeightForWidth())
        self.button9.setSizePolicy(sizePolicy)
        self.button9.setMaximumSize(QtCore.QSize(20, 16777215))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.button9.setFont(font)
        self.button9.setFlat(True)
        self.button9.setObjectName('button9')
        self.horizontalLayout_7.addWidget(self.button9)
        self.button10 = QtWidgets.QPushButton(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.button10.sizePolicy().hasHeightForWidth())
        self.button10.setSizePolicy(sizePolicy)
        self.button10.setMaximumSize(QtCore.QSize(20, 16777215))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.button10.setFont(font)
        self.button10.setFlat(True)
        self.button10.setObjectName('button10')
        self.horizontalLayout_7.addWidget(self.button10)
        self.button12 = QtWidgets.QPushButton(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.button12.sizePolicy().hasHeightForWidth())
        self.button12.setSizePolicy(sizePolicy)
        self.button12.setMaximumSize(QtCore.QSize(20, 16777215))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.button12.setFont(font)
        self.button12.setFlat(True)
        self.button12.setObjectName('button12')
        self.horizontalLayout_7.addWidget(self.button12)
        self.button3 = QtWidgets.QPushButton(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.button3.sizePolicy().hasHeightForWidth())
        self.button3.setSizePolicy(sizePolicy)
        self.button3.setMaximumSize(QtCore.QSize(20, 16777215))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.button3.setFont(font)
        self.button3.setFlat(True)
        self.button3.setObjectName('button3')
        self.horizontalLayout_7.addWidget(self.button3)
        self.button11 = QtWidgets.QPushButton(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.button11.sizePolicy().hasHeightForWidth())
        self.button11.setSizePolicy(sizePolicy)
        self.button11.setMaximumSize(QtCore.QSize(20, 16777215))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.button11.setFont(font)
        self.button11.setFlat(True)
        self.button11.setObjectName('button11')
        self.horizontalLayout_7.addWidget(self.button11)
        self.button4 = QtWidgets.QPushButton(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.button4.sizePolicy().hasHeightForWidth())
        self.button4.setSizePolicy(sizePolicy)
        self.button4.setMaximumSize(QtCore.QSize(20, 16777215))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.button4.setFont(font)
        self.button4.setFlat(True)
        self.button4.setObjectName('button4')
        self.horizontalLayout_7.addWidget(self.button4)
        self.button6 = QtWidgets.QPushButton(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.button6.sizePolicy().hasHeightForWidth())
        self.button6.setSizePolicy(sizePolicy)
        self.button6.setMaximumSize(QtCore.QSize(20, 16777215))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.button6.setFont(font)
        self.button6.setFlat(True)
        self.button6.setObjectName('button6')
        self.horizontalLayout_7.addWidget(self.button6)
        self.horizontalLayout_6.addWidget(self.frame)
        self.verticalLayout_2.addLayout(self.horizontalLayout_6)
        spacerItem4 = QtWidgets.QSpacerItem(
            20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem4)
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
        self.paintSizeSlider.setProperty('value', 25)
        self.paintSizeSlider.setOrientation(QtCore.Qt.Horizontal)
        self.paintSizeSlider.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.paintSizeSlider.setObjectName('paintSizeSlider')
        self.horizontalLayout_5.addWidget(self.paintSizeSlider)
        self.verticalLayout.addLayout(self.horizontalLayout_5)
        spacerItem5 = QtWidgets.QSpacerItem(
            20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem5)
        self.toolSettingsStackedWidget.addWidget(self.pageCircle)
        self.pageKeycodes = QtWidgets.QWidget()
        self.pageKeycodes.setObjectName('pageKeycodes')
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.pageKeycodes)
        self.verticalLayout_3.setObjectName('verticalLayout_3')
        self.toolSettingsStackedWidget.addWidget(self.pageKeycodes)
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
        self.menuEdit = QtWidgets.QMenu(self.menubar)
        self.menuEdit.setObjectName('menuEdit')
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
        self.actionSave_screenshoot = QtWidgets.QAction(MainWindow)
        self.actionSave_screenshoot.setObjectName('actionSave_screenshoot')
        self.menuMenu.addAction(self.actionOtworzLokacje)
        self.menuMenu.addAction(self.actionZapisz)
        self.menuMenu.addAction(self.actionZamknijProgram)
        self.menuEdit.addAction(self.actionSave_screenshoot)
        self.menubar.addAction(self.menuMenu.menuAction())
        self.menubar.addAction(self.menuEdit.menuAction())
        self.menubar.addAction(self.menuPomoc.menuAction())

        self.retranslateUi(MainWindow)
        self.toolSettingsStackedWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate(
            'MainWindow', 'YAYA - YOLO annoter'))
        self.isSavedCheckBox.setText(_translate('MainWindow', 'Saved'))
        self.isErrorsCheckBox.setText(_translate('MainWindow', 'isErrors?'))
        self.label_4.setText(_translate('MainWindow', 'Image scaling:'))
        self.imageScalingComboBox.setItemText(
            0, _translate('MainWindow', 'Resize'))
        self.imageScalingComboBox.setItemText(
            1, _translate('MainWindow', 'ResizeAspectRatio'))
        self.imageScalingComboBox.setItemText(
            2, _translate('MainWindow', 'OriginalSize'))
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
            _translate('MainWindow', '(S)ave'))
        self.SaveFileAnnotationsButton.setShortcut(
            _translate('MainWindow', 'S'))
        self.DeleteImageAnnotationsButton.setText(
            _translate('MainWindow', '(X)Delete'))
        self.DeleteImageAnnotationsButton.setShortcut(
            _translate('MainWindow', 'X'))
        self.DeleteNotAnnotatedFilesButton.setText(
            _translate('MainWindow', 'Delete not annotated'))
        self.fileSummaryLabel.setText(_translate('MainWindow', 'TextLabel'))
        self.fileSelectorTableWidget.setSortingEnabled(True)
        self.label.setText(_translate('MainWindow', 'Annotations'))
        self.addAnnotationsButton.setText(_translate('MainWindow', '(A)dd '))
        self.addAnnotationsButton.setShortcut(_translate('MainWindow', 'A'))
        self.renameAnnotationsButton.setText(
            _translate('MainWindow', 'Re(N)ame'))
        self.renameAnnotationsButton.setShortcut(_translate('MainWindow', 'N'))
        self.removeAnnotationsButton.setText(
            _translate('MainWindow', '(R)emove'))
        self.removeAnnotationsButton.setShortcut(_translate('MainWindow', 'R'))
        self.ClearAnnotationsButton.setText(
            _translate('MainWindow', '(C)lear'))
        self.ClearAnnotationsButton.setShortcut(_translate('MainWindow', 'C'))
        self.hideLabelsButton.setText(
            _translate('MainWindow', '(L)abels hide'))
        self.hideLabelsButton.setShortcut(_translate('MainWindow', 'L'))
        self.hideAnnotationsButton.setText(_translate('MainWindow', '(H)ide'))
        self.hideAnnotationsButton.setShortcut(_translate('MainWindow', 'H'))
        self.detectAnnotationsButton.setText(
            _translate('MainWindow', '(D)etect '))
        self.detectAnnotationsButton.setShortcut(_translate('MainWindow', 'D'))
        self.label_3.setText(_translate('MainWindow', 'Painting'))
        self.paintCircleButton.setText(_translate('MainWindow', 'Circl(e)'))
        self.paintCircleButton.setShortcut(_translate('MainWindow', 'E'))
        self.detectorClassesLabel.setText(_translate(
            'MainWindow', 'Selected detector classes :'))
        self.button2.setText(_translate('MainWindow', '2'))
        self.button2.setShortcut(_translate('MainWindow', '2'))
        self.button5.setText(_translate('MainWindow', '5'))
        self.button5.setShortcut(_translate('MainWindow', '5'))
        self.button7.setText(_translate('MainWindow', '7'))
        self.button7.setShortcut(_translate('MainWindow', '7'))
        self.button8.setText(_translate('MainWindow', '8'))
        self.button8.setShortcut(_translate('MainWindow', '8'))
        self.button1.setText(_translate('MainWindow', '1'))
        self.button1.setShortcut(_translate('MainWindow', '1'))
        self.buttonOffset.setText(_translate('MainWindow', '`'))
        self.buttonOffset.setShortcut(_translate('MainWindow', '`'))
        self.button9.setText(_translate('MainWindow', '9'))
        self.button9.setShortcut(_translate('MainWindow', '9'))
        self.button10.setText(_translate('MainWindow', '10'))
        self.button10.setShortcut(_translate('MainWindow', '0'))
        self.button12.setText(_translate('MainWindow', '12'))
        self.button12.setShortcut(_translate('MainWindow', '='))
        self.button3.setText(_translate('MainWindow', '3'))
        self.button3.setShortcut(_translate('MainWindow', '3'))
        self.button11.setText(_translate('MainWindow', '11'))
        self.button11.setShortcut(_translate('MainWindow', '-'))
        self.button4.setText(_translate('MainWindow', '4'))
        self.button4.setShortcut(_translate('MainWindow', '4'))
        self.button6.setText(_translate('MainWindow', '6'))
        self.button6.setShortcut(_translate('MainWindow', '6'))
        self.paintLabel.setText(_translate('MainWindow', 'Painting Size'))
        self.menuMenu.setTitle(_translate('MainWindow', 'File'))
        self.menuPomoc.setTitle(_translate('MainWindow', 'Help'))
        self.menuEdit.setTitle(_translate('MainWindow', 'Edit'))
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
        self.actionSave_screenshoot.setText(
            _translate('MainWindow', 'Save screenshoot'))
        self.actionSave_screenshoot.setShortcut(
            _translate('MainWindow', 'Shift+S'))
