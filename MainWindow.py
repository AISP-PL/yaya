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
    QListWidgetItem
from PyQt5 import QtCore, QtGui
from engine.annote import GetClasses
from ViewerEditorImage import ViewerEditorImage


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

        # Open File
        self.OpenFile()

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

        # Buttons
        self.ui.nextFileButton.clicked.connect(self.CallbackNextFile)
        self.ui.prevFileButton.clicked.connect(self.CallbackPrevFile)
        self.ui.SaveFileAnnotationsButton.clicked.connect(
            self.CallbackSaveFileAnnotationsButton)
        self.ui.ClearAnnotationsButton.clicked.connect(
            self.CallbackClearAnnotationsButton)
        self.ui.DeleteImageAnnotationsButton.clicked.connect(
            self.CallbackDeleteImageAnnotationsButton)
        self.ui.hideAnnotationsButton.clicked.connect(
            self.CallbackHideAnnotationsButton)
        self.ui.removeAnnotationsButton.clicked.connect(
            self.CallbackRemoveAnnotationsButton)
        self.ui.detectAnnotationsButton.clicked.connect(
            self.CallbackDetectAnnotations)

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

        # Setup isSaved tick
        if (self.annoter.IsSynchronized()):
            self.ui.isSavedCheckBox.setChecked(True)
        else:
            self.ui.isSavedCheckBox.setChecked(False)

        # Setup viewer/editor
        self.ui.viewerEditor.SetAnnoter(self.annoter)
        self.ui.viewerEditor.SetImage(self.annoter.GetImage())

    def OpenFile(self):
        ''' Sets default for UI.'''

    def SaveFile(self, fileEntry):
        ''' Sets default for UI.'''

    def Run(self):
        '''  Run gui window thread and return exit code.'''
        self.window.show()
        return self.App.exec_()

    def CallbackLabelsRowChanged(self, index):
        ''' Current labels row changed. '''
        self.ui.viewerEditor.SetClassNumber(index)

    def CallbackFileNumberSlider(self):
        ''' Callback for changed of file number slider.'''
        # Read current file number
        fileNumber = self.ui.fileNumberSlider.value()
        # Update annoter
        self.annoter.SetImageNumber(fileNumber)
        # Setup UI again
        self.Setup()

    def CallbackDetectAnnotations(self):
        ''' Detect annotations.'''
        self.annoter.Process(forceDetector=True)
        self.Setup()

    def CallbackRemoveAnnotationsButton(self):
        ''' Remove annotations.'''
        self.ui.viewerEditor.SetEditorMode(
            ViewerEditorImage.ModeEditorRemoveAnnotation)

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
