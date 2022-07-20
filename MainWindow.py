'''
Created on 29 gru 2020

@author: spasz
'''
import sys
import os
import glob
import logging
import subprocess
import cv2
from Ui_MainWindow import Ui_MainWindow
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QTableWidgetItem,\
    QListWidgetItem, QButtonGroup
from PyQt5 import QtCore, QtGui
from engine.annote import GetClasses
from ViewerEditorImage import ViewerEditorImage
from helpers.files import FixPath


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

        # Create
        # - QtApplication
        # - Qt UI
        # - QtMainWindow
        self.App = QApplication(sys.argv)
        self.ui = Ui_MainWindow()
        self.window = QMainWindow()
        # The main window object calls the setupUi method to set the QMainWindow object
        self.ui.setupUi(self.window)

        # Setup all
        self.SetupDefault()
        self.Setup()

    def SetupDefault(self):
        ''' Sets default for UI.'''
        # Annoter - process first time.
        self.annoter.Process()
        # Read annoter results
        imageNumber = self.annoter.GetImageNumber()
        imageCount = self.annoter.GetImagesCount()

        # List of detector labels - Create
        for className in GetClasses():
            self.ui.labelsListWidget.addItem(
                QListWidgetItem(className, self.ui.labelsListWidget))
        self.ui.labelsListWidget.setCurrentRow(0)
        self.ui.labelsListWidget.currentRowChanged.connect(
            self.CallbackLabelsRowChanged)

        # File number slider - create
        self.ui.fileNumberSlider.setMaximum(imageCount)
        self.ui.fileNumberSlider.setValue(imageNumber)
        self.ui.fileNumberSlider.valueChanged.connect(
            self.CallbackFileNumberSlider)

        # Paint size slider
        self.ui.paintSizeSlider.valueChanged.connect(
            self.CallbackPaintSizeSlider)
        
        # Setup files selector table widget
        labels = ['Filepath', 'Annotations']
        self.ui.fileSelectorTableWidget.setColumnCount(len(labels))
        self.ui.fileSelectorTableWidget.setHorizontalHeaderLabels(labels)
        self.ui.fileSelectorTableWidget.setRowCount(self.annoter.GetImagesCount())
        for rowIndex, fileEntry in enumerate(self.annoter.GetImagesList()):
            # Start from column zero
            colIndex = 0
            
            # Filepath column
            item = QTableWidgetItem(str(fileEntry))
            item.setToolTip(str(rowIndex))
            self.ui.fileSelectorTableWidget.setItem(rowIndex, colIndex, item)
            colIndex += 1
            
            # Annotations column
            item = QTableWidgetItem(str(0))
            item.setToolTip(str(rowIndex))
            self.ui.fileSelectorTableWidget.setItem(rowIndex, colIndex, item)
            colIndex += 1
        self.ui.fileSelectorTableWidget.itemClicked.connect(
            self.CallbackFileSelectorItemClicked)
        
        # Menu handling
        self.ui.actionZamknijProgram.triggered.connect(self.CallbackClose)
        self.ui.actionZapisz.triggered.connect(self.CallbackSaveFileAnnotationsButton)
        self.ui.actionOtworzLokacje.triggered.connect(self.CallbackOpenLocation)

        # Buttons group - for mode buttons
        self.modeButtonGroup = QButtonGroup(self.window)
        self.modeButtonGroup.addButton(self.ui.addAnnotationsButton)
        self.modeButtonGroup.addButton(self.ui.removeAnnotationsButton)
        self.modeButtonGroup.addButton(self.ui.paintCircleButton)

        # Buttons player
        self.ui.nextFileButton.clicked.connect(self.CallbackNextFile)
        self.ui.prevFileButton.clicked.connect(self.CallbackPrevFile)
        # Buttons Image
        self.ui.SaveFileAnnotationsButton.clicked.connect(
            self.CallbackSaveFileAnnotationsButton)
        self.ui.DeleteImageAnnotationsButton.clicked.connect(
            self.CallbackDeleteImageAnnotationsButton)
        # Buttons - Annotations
        self.ui.addAnnotationsButton.clicked.connect(
            self.CallbackAddAnnotationsButton)
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
        self.ui.button1.clicked.connect(lambda: self.CallbackKeycodeButtonClicked(self.ui.button1)) 
        self.ui.button2.clicked.connect(lambda: self.CallbackKeycodeButtonClicked(self.ui.button2)) 
        self.ui.button3.clicked.connect(lambda: self.CallbackKeycodeButtonClicked(self.ui.button3)) 
        self.ui.button4.clicked.connect(lambda: self.CallbackKeycodeButtonClicked(self.ui.button4)) 
        self.ui.button5.clicked.connect(lambda: self.CallbackKeycodeButtonClicked(self.ui.button5)) 
        self.ui.button6.clicked.connect(lambda: self.CallbackKeycodeButtonClicked(self.ui.button6)) 
        self.ui.button7.clicked.connect(lambda: self.CallbackKeycodeButtonClicked(self.ui.button7)) 
        self.ui.button8.clicked.connect(lambda: self.CallbackKeycodeButtonClicked(self.ui.button8)) 
        self.ui.button9.clicked.connect(lambda: self.CallbackKeycodeButtonClicked(self.ui.button9)) 
        self.ui.button10.clicked.connect(lambda: self.CallbackKeycodeButtonClicked(self.ui.button10)) 
        self.ui.button11.clicked.connect(lambda: self.CallbackKeycodeButtonClicked(self.ui.button11)) 
        self.ui.button12.clicked.connect(lambda: self.CallbackKeycodeButtonClicked(self.ui.button12)) 

    def Setup(self):
        ''' Setup again UI.'''
        filename = self.annoter.GetFilename()
        imageWidth, imageHeight, imageBytes = self.annoter.GetImageSize()
        imageNumber = self.annoter.GetImageNumber()
        imageCount = self.annoter.GetImagesCount()

        # Setup horizontal file slider
        self.ui.fileNumberSliderLabel.setText(
            '%u/%u' % (imageNumber, imageCount))

        # Setup file info
        self.ui.fileLabel.setText('[%upx x %upx x %uB] %s' % (imageWidth,
                                                              imageHeight,
                                                              imageBytes,
                                                              filename))

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
    
    def CallbackKeycodeButtonClicked(self, button):
        ''' Callback when keycode button clicked.'''
        indexChr = int(button.text())-1
        self.ui.labelsListWidget.setCurrentRow(indexChr)

    def CallbackLabelsRowChanged(self, index):
        ''' Current labels row changed. '''
        self.ui.viewerEditor.SetClassNumber(index)
    
    def CallbackFileSelectorItemClicked(self, item):
        ''' When file selector item was clicked.'''
        # Read current file number
        fileNumber = int(item.toolTip())
        self.ui.fileNumberSlider.setValue(fileNumber)
        # # Update annoter
        # self.annoter.SetImageNumber(fileNumber)
        # # Setup UI again
        # self.Setup()

    def CallbackFileNumberSlider(self):
        ''' Callback for changed of file number slider.'''
        # Read current file number
        fileNumber = self.ui.fileNumberSlider.value()
        # Update annoter
        self.annoter.SetImageNumber(fileNumber)
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
        self.annoter.Delete()
        self.annoter.Process()
        self.Setup()

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
