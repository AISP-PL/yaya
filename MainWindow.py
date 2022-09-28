'''
Created on 29 gru 2020

@author: spasz
'''
import sys
import os
import logging
from Ui_MainWindow import Ui_MainWindow
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QTableWidgetItem,\
    QListWidgetItem, QButtonGroup, QMessageBox
from PyQt5 import QtCore, QtGui
from engine.annote import GetClasses
from ViewerEditorImage import ViewerEditorImage
from helpers.files import FixPath
from copy import copy
from PyQt5.QtCore import Qt


class MainWindowGui(Ui_MainWindow):
    '''
    classdocs
    '''

    def __init__(self,
                 args,
                 detector,
                 annoter,
                 ):
        '''
        Constructor
        '''
        # Config
        self.info = {'Callbacks': True}
        # Store initial arguments
        self.args = args
        # Store detector handle
        self.detector = detector
        # Store annoter handle
        self.annoter = annoter
        # Keys offset
        self.keysOffset = 0
        # Keys length
        self.keysSize = 12

        # UI - creation
        self.App = QApplication(sys.argv)
        self.ui = Ui_MainWindow()
        self.window = QMainWindow()
        self.ui.setupUi(self.window)

        # Setup all
        self.SetupDefault()
        self.Setup()

    def ImageIDToRowNumber(self, imageID):
        ''' Image number to row index.'''
        # Found index
        foundIndex = None

        # Find rowIndex of imageNumber
        for rowIndex in range(self.ui.fileSelectorTableWidget.rowCount()):
            item = self.ui.fileSelectorTableWidget.item(rowIndex, 0)
            if (int(item.toolTip()) == imageID):
                foundIndex = rowIndex
                break

        return foundIndex

    def SetupDefault(self):
        ''' Sets default for UI.'''
        # Annoter - process first time.
        self.annoter.Process()

        # Image scaling
        self.ui.imageScalingComboBox.currentTextChanged.connect(
            self.CallbackImageScalingTextChanged)

        # List of detector labels - Create
        for className in GetClasses():
            self.ui.labelsListWidget.addItem(
                QListWidgetItem(className, self.ui.labelsListWidget))
        self.ui.labelsListWidget.setCurrentRow(0)
        self.ui.labelsListWidget.currentRowChanged.connect(
            self.CallbackLabelsRowChanged)

        # Paint size slider
        self.ui.paintSizeSlider.valueChanged.connect(
            self.CallbackPaintSizeSlider)

        # Setup files selector table widget
        labels = ['Name', 'IsAnnotated', 'Annotations',
                  'TP', 'FP', 'FN', 'Precision', 'Recall',
                  'LTP', 'LTN', 'Errors']
        self.ui.fileSelectorTableWidget.setColumnCount(len(labels))
        self.ui.fileSelectorTableWidget.setHorizontalHeaderLabels(labels)
        self.ui.fileSelectorTableWidget.setRowCount(
            self.annoter.GetFilesCount())
        for rowIndex, fileEntry in enumerate(self.annoter.GetFiles()):
            # Start from column zero
            colIndex = 0

            # Filename column
            item = QTableWidgetItem(str(fileEntry['Name']))
            item.setToolTip(str(fileEntry['ID']))
            self.ui.fileSelectorTableWidget.setItem(rowIndex, colIndex, item)
            colIndex += 1

            # IsAnnotation column
            item = QTableWidgetItem(str(fileEntry['IsAnnotation']))
            if (fileEntry['IsAnnotation']):
                item.setBackground(Qt.green)
            else:
                item.setBackground(Qt.red)
            item.setToolTip(str(fileEntry['ID']))
            self.ui.fileSelectorTableWidget.setItem(rowIndex, colIndex, item)
            colIndex += 1

            # Annotations column
            item = QTableWidgetItem(str(len(fileEntry['Annotations'])))
            item.setToolTip(str(fileEntry['ID']))
            self.ui.fileSelectorTableWidget.setItem(rowIndex, colIndex, item)
            colIndex += 1

            # TP column
            item = QTableWidgetItem(str(fileEntry['TP']))
            item.setToolTip(str(fileEntry['ID']))
            self.ui.fileSelectorTableWidget.setItem(rowIndex, colIndex, item)
            colIndex += 1

            # FP column
            item = QTableWidgetItem(str(fileEntry['FP']))
            item.setToolTip(str(fileEntry['ID']))
            self.ui.fileSelectorTableWidget.setItem(rowIndex, colIndex, item)
            colIndex += 1

            # FN column
            item = QTableWidgetItem(str(fileEntry['FN']))
            item.setToolTip(str(fileEntry['ID']))
            self.ui.fileSelectorTableWidget.setItem(rowIndex, colIndex, item)
            colIndex += 1

            # Precision column
            item = QTableWidgetItem(str(fileEntry['Precision']))
            item.setToolTip(str(fileEntry['ID']))
            self.ui.fileSelectorTableWidget.setItem(rowIndex, colIndex, item)
            colIndex += 1

            # Recall column
            item = QTableWidgetItem(str(fileEntry['Recall']))
            item.setToolTip(str(fileEntry['ID']))
            self.ui.fileSelectorTableWidget.setItem(rowIndex, colIndex, item)
            colIndex += 1

            # LTP column
            item = QTableWidgetItem(str(fileEntry['LTP']))
            item.setToolTip(str(fileEntry['ID']))
            self.ui.fileSelectorTableWidget.setItem(rowIndex, colIndex, item)
            colIndex += 1

            # LTN column
            item = QTableWidgetItem(str(fileEntry['LTN']))
            item.setToolTip(str(fileEntry['ID']))
            self.ui.fileSelectorTableWidget.setItem(rowIndex, colIndex, item)
            colIndex += 1

            # Errors column
            item = QTableWidgetItem(str(fileEntry['Errors']))
            item.setToolTip(str(fileEntry['ID']))
            self.ui.fileSelectorTableWidget.setItem(rowIndex, colIndex, item)
            colIndex += 1

        self.ui.fileSelectorTableWidget.itemClicked.connect(
            self.CallbackFileSelectorItemClicked)

        # Menu handling
        self.ui.actionZamknijProgram.triggered.connect(self.CallbackClose)
        self.ui.actionZapisz.triggered.connect(
            self.CallbackSaveFileAnnotationsButton)
        self.ui.actionOtworzLokacje.triggered.connect(
            self.CallbackOpenLocation)

        # Buttons group - for mode buttons
        self.modeButtonGroup = QButtonGroup(self.window)
        self.modeButtonGroup.addButton(self.ui.addAnnotationsButton)
        self.modeButtonGroup.addButton(self.ui.removeAnnotationsButton)
        self.modeButtonGroup.addButton(self.ui.paintCircleButton)
        self.modeButtonGroup.addButton(self.ui.renameAnnotationsButton)

        # Buttons player
        self.ui.nextFileButton.clicked.connect(self.CallbackNextFile)
        self.ui.prevFileButton.clicked.connect(self.CallbackPrevFile)
        # Buttons Image
        self.ui.SaveFileAnnotationsButton.clicked.connect(
            self.CallbackSaveFileAnnotationsButton)
        self.ui.DeleteImageAnnotationsButton.clicked.connect(
            self.CallbackDeleteImageAnnotationsButton)
        self.ui.DeleteNotAnnotatedFilesButton.clicked.connect(
            self.CallbackDeleteNotAnnotatedFilesButton)
        # Buttons - Annotations
        self.ui.addAnnotationsButton.clicked.connect(
            self.CallbackAddAnnotationsButton)
        self.ui.renameAnnotationsButton.clicked.connect(
            self.CallbackRenameAnnotationsButton)
        self.ui.removeAnnotationsButton.clicked.connect(
            self.CallbackRemoveAnnotationsButton)
        self.ui.detectAnnotationsButton.clicked.connect(
            self.CallbackDetectAnnotations)
        self.ui.hideAnnotationsButton.clicked.connect(
            self.CallbackHideAnnotationsButton)
        self.ui.ClearAnnotationsButton.clicked.connect(
            self.CallbackClearAnnotationsButton)
        # Buttons - Painting
        self.ui.paintCircleButton.clicked.connect(
            self.CallbackPaintCircleButton)
        # Buttons - list of gui key codes
        self.ui.button1.clicked.connect(
            lambda: self.CallbackKeycodeButtonClicked(self.ui.button1))
        self.ui.button2.clicked.connect(
            lambda: self.CallbackKeycodeButtonClicked(self.ui.button2))
        self.ui.button3.clicked.connect(
            lambda: self.CallbackKeycodeButtonClicked(self.ui.button3))
        self.ui.button4.clicked.connect(
            lambda: self.CallbackKeycodeButtonClicked(self.ui.button4))
        self.ui.button5.clicked.connect(
            lambda: self.CallbackKeycodeButtonClicked(self.ui.button5))
        self.ui.button6.clicked.connect(
            lambda: self.CallbackKeycodeButtonClicked(self.ui.button6))
        self.ui.button7.clicked.connect(
            lambda: self.CallbackKeycodeButtonClicked(self.ui.button7))
        self.ui.button8.clicked.connect(
            lambda: self.CallbackKeycodeButtonClicked(self.ui.button8))
        self.ui.button9.clicked.connect(
            lambda: self.CallbackKeycodeButtonClicked(self.ui.button9))
        self.ui.button10.clicked.connect(
            lambda: self.CallbackKeycodeButtonClicked(self.ui.button10))
        self.ui.button11.clicked.connect(
            lambda: self.CallbackKeycodeButtonClicked(self.ui.button11))
        self.ui.button12.clicked.connect(
            lambda: self.CallbackKeycodeButtonClicked(self.ui.button12))
        self.ui.buttonOffset.clicked.connect(
            self.CallbackKeycodeOffsetButtonClicked)

    def Setup(self):
        ''' Setup again UI.'''
        filename = self.annoter.GetFilename()
        imageWidth, imageHeight, imageBytes = self.annoter.GetImageSize()
        imageNumber = self.annoter.GetFileIndex()
        imageID = self.annoter.GetFileID()
        imageCount = self.annoter.GetFilesCount()
        imageAnnotatedCount = self.annoter.GetFilesAnnotatedCount()

        # Setup progress bar
        self.ui.progressBar.setMinimum(0)
        self.ui.progressBar.setMaximum(imageCount)
        self.ui.progressBar.setValue(imageAnnotatedCount)

        # Setup horizontal file slider
        self.ui.fileNumberSliderLabel.setText(
            'ID%u (%u/%u)' % (imageID, imageNumber, imageCount))

        # Setup file info
        self.ui.fileLabel.setText('[%upx x %upx x %uB] %s' % (imageWidth,
                                                              imageHeight,
                                                              imageBytes,
                                                              filename))

        # Setup files selector table widget
        fileEntry = self.annoter.GetFile()

        # Find rowIndex of imageNumber
        rowIndex = self.ImageIDToRowNumber(imageID)

        if (fileEntry is not None):
            # Filename column
            self.ui.fileSelectorTableWidget.item(rowIndex, 0)
            # IsAnnotation column
            item = self.ui.fileSelectorTableWidget.item(
                rowIndex, 1)
            if (fileEntry['IsAnnotation']):
                item.setBackground(Qt.green)
            else:
                item.setBackground(Qt.red)
            item.setText(str(fileEntry['IsAnnotation']))
            # Annotations column
            self.ui.fileSelectorTableWidget.item(
                rowIndex, 2).setText(str(len(fileEntry['Annotations'])))
            # TP column
            self.ui.fileSelectorTableWidget.item(
                rowIndex, 3).setText(str(fileEntry['TP']))
            # TN column
            self.ui.fileSelectorTableWidget.item(
                rowIndex, 4).setText(str(fileEntry['FP']))
            # FN column
            self.ui.fileSelectorTableWidget.item(
                rowIndex, 5).setText(str(fileEntry['FN']))
            # Precision column
            self.ui.fileSelectorTableWidget.item(
                rowIndex, 6).setText(str(fileEntry['Precision']))
            # Recall column
            self.ui.fileSelectorTableWidget.item(
                rowIndex, 7).setText(str(fileEntry['Recall']))
            # LTP column
            self.ui.fileSelectorTableWidget.item(
                rowIndex, 8).setText(str(fileEntry['LTP']))
            # LTN Surplus column
            self.ui.fileSelectorTableWidget.item(
                rowIndex, 9).setText(str(fileEntry['LTN']))
            # Errors column
            self.ui.fileSelectorTableWidget.item(
                rowIndex, 10).setText(str(fileEntry['Errors']))

        # Setup files selector table widget
        self.ui.fileSelectorTableWidget.clearSelection()
        if (imageCount != 0):
            # Select whole row with image
            for i in range(self.ui.fileSelectorTableWidget.columnCount()):
                item = self.ui.fileSelectorTableWidget.item(rowIndex, i)
                item.setSelected(True)

#             Move verticall scroll bar also
#             self.ui.fileSelectorTableWidget.verticalScrollBar().setValue(rowIndex)

        # Paint size slider
        self.ui.paintLabel.setText('Paint size %u' %
                                   self.ui.paintSizeSlider.value())

        # Setup isSaved tick
        if (self.annoter.IsSynchronized()):
            self.ui.isSavedCheckBox.setChecked(True)
        else:
            self.ui.isSavedCheckBox.setChecked(False)

        # Setup errors tick
        errors = self.annoter.GetErrors()
        if (len(errors) != 0):
            self.ui.isErrorsCheckBox.setChecked(True)
        else:
            self.ui.isErrorsCheckBox.setChecked(False)

        # Setup viewer/editor
        self.ui.viewerEditor.SetAnnoter(self.annoter)
        self.ui.viewerEditor.SetImage(self.annoter.GetImage())

    def Run(self):
        '''  Run gui window thread and return exit code.'''
        self.window.show()
        return self.App.exec_()

    def CallbackImageScalingTextChanged(self, text):
        ''' Callback when image scaling text changed.'''
        if (text == 'Resize'):
            self.ui.viewerEditor.SetImageScaling(
                ViewerEditorImage.ImageScalingResize)
        elif (text == 'ResizeAspectRatio'):
            self.ui.viewerEditor.SetImageScaling(
                ViewerEditorImage.ImageScalingResizeAspectRatio)
        elif (text == 'OriginalSize'):
            self.ui.viewerEditor.SetImageScaling(
                ViewerEditorImage.ImageScalingOriginalSize)
        else:
            logging.error('(MainWindow) Unknown value!')

    def CallbackKeycodeOffsetButtonClicked(self):
        ''' Callback when keycode offset button clicked.'''
        self.keysOffset += self.keysSize
        if (self.keysOffset >= self.ui.labelsListWidget.count()):
            self.keysOffset = 0
        # Call like button 1 clicked
        self.CallbackKeycodeButtonClicked(self.ui.button1)

    def CallbackKeycodeButtonClicked(self, button):
        ''' Callback when keycode button clicked.'''
        indexChr = self.keysOffset + int(button.text())-1
        if (indexChr >= self.ui.labelsListWidget.count()):
            indexChr = self.ui.labelsListWidget.count()-1

        self.ui.labelsListWidget.setCurrentRow(indexChr)

    def CallbackLabelsRowChanged(self, index):
        ''' Current labels row changed. '''
        self.ui.viewerEditor.SetClassNumber(index)

    def CallbackFileSelectorItemClicked(self, item):
        ''' When file selector item was clicked.'''
        # Read current file number
        fileID = int(item.toolTip())
        # Update annoter
        self.annoter.SetImageID(fileID)
        # Setup UI again
        self.Setup()

    def CallbackPaintSizeSlider(self):
        ''' Paint size slider changed.'''
        self.ui.viewerEditor.SetEditorModeArgument(
            self.ui.paintSizeSlider.value())
        self.Setup()

    def CallbackPaintCircleButton(self):
        ''' Paint circle button.'''
        self.ui.toolSettingsStackedWidget.setCurrentWidget(self.ui.pageCircle)
        self.ui.viewerEditor.SetEditorMode(ViewerEditorImage.ModePaintCircle,
                                           argument=self.ui.paintSizeSlider.value())

    def CallbackDetectAnnotations(self):
        ''' Detect annotations.'''
        self.annoter.Process(forceDetector=True)
        self.Setup()

    def CallbackAddAnnotationsButton(self):
        ''' Remove annotations.'''
        self.ui.toolSettingsStackedWidget.setCurrentWidget(
            self.ui.pageAnnotations)
        self.ui.viewerEditor.SetEditorMode(
            ViewerEditorImage.ModeAddAnnotation)

    def CallbackRenameAnnotationsButton(self):
        ''' Remove annotations.'''
        self.ui.toolSettingsStackedWidget.setCurrentWidget(
            self.ui.pageAnnotations)
        self.ui.viewerEditor.SetEditorMode(
            ViewerEditorImage.ModeRenameAnnotation)

    def CallbackRemoveAnnotationsButton(self):
        ''' Remove annotations.'''
        self.ui.toolSettingsStackedWidget.setCurrentWidget(
            self.ui.pageAnnotations)
        self.ui.viewerEditor.SetEditorMode(
            ViewerEditorImage.ModeRemoveAnnotation)

    def CallbackHideAnnotationsButton(self):
        '''Callback'''
        self.ui.viewerEditor.SetOption('isAnnotationsHidden',
                                       not self.ui.viewerEditor.GetOption('isAnnotationsHidden'))

    def CallbackSaveFileAnnotationsButton(self):
        '''Callback'''
        self.annoter.Save()
        self.Setup()

    def CallbackClearAnnotationsButton(self):
        '''Callback'''
        self.annoter.ClearAnnotations()
        self.Setup()

    def CallbackDeleteImageAnnotationsButton(self):
        '''Callback'''
        # Remove QtableWidget row
        rowIndex = self.ImageIDToRowNumber(self.annoter.GetFileID())
        if (rowIndex is not None):
            self.ui.fileSelectorTableWidget.removeRow(rowIndex)
            # Remove annoter data
            self.annoter.Delete()
            self.annoter.Process()
            self.Setup()

    def CallbackDeleteNotAnnotatedFilesButton(self):
        ''' Callback.'''
        button_reply = QMessageBox.question(self.window,
                                            'Delete all not annotated images',
                                            'Are you sure (delete not annotated) ?')
        if button_reply == QMessageBox.Yes:
            filesList = copy(self.annoter.GetFiles())
            for fileEntry in filesList:
                if (fileEntry['IsAnnotation'] is False):
                    self.annoter.Delete(fileEntry)

    def CallbackNextFile(self):
        '''Callback'''
        self.annoter.ProcessNext()
        self.Setup()

    def CallbackPrevFile(self):
        '''Callback'''
        self.annoter.ProcessPrev()
        self.Setup()

    def CallbackOpenLocation(self):
        ''' Open location callback.'''
        filepath = str(QFileDialog.getExistingDirectory(
            None, 'Select Directory'))
        self.annoter.OpenLocation(FixPath(filepath))
        self.SetupDefault()
        self.Setup()

    def CallbackClose(self):
        ''' Close GUI callback.'''
        logging.debug('Closing application!')
        self.window.close()
