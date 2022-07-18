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
        for className in GetClasses():
            self.ui.labelsListWidget.addItem(
                QListWidgetItem(className, self.ui.labelsListWidget))

    def Setup(self):
        ''' Sets default for UI.'''
        filename = self.annoter.GetFilename()
        imageNumber = self.annoter.GetImageNumber()
        imageCount = self.annoter.GetImagesCount()

        # Setup horizontal file slider
        self.ui.fileNumberSliderLabel.setText(
            '%u/%u' % (imageNumber, imageCount))
        self.ui.fileNumberSlider.setMaximum(imageCount)
        self.ui.fileNumberSlider.setValue(imageNumber)
        self.ui.fileNumberSlider.valueChanged.connect(
            self.CallbackFileNumberSlider)

        # Setup filename
        self.ui.fileLabel.setText('%s' % (filename))

    def OpenFile(self):
        ''' Sets default for UI.'''

    def SaveFile(self, fileEntry):
        ''' Sets default for UI.'''

    def Run(self):
        '''  Run gui window thread and return exit code.'''
        self.window.show()
        return self.App.exec_()

    def CallbackFileNumberSlider(self):
        ''' Callback for file number slider.'''
        self.ui.fileNumberSliderLabel.setText('%u/%u' % (self.ui.fileNumberSlider.value(),
                                                         self.ui.fileNumberSlider.maximum()))
