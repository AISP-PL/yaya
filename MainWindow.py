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
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QTableWidgetItem
from PyQt5 import QtCore, QtGui


class MainWindowGui(Ui_MainWindow):
    '''
    classdocs
    '''

    def __init__(self, args):
        '''
        Constructor
        '''
        # Config
        self.info = {'Callbacks': True}
        # Store initial arguments
        self.args = args
        # Input filepath
        self.filepath = None
        # File feeder with all readed location data
        self.feeder = None
        # current location path
        self.location = None
        # Default disabled detector classes
        self.defaultDisabledClasses = [
            'i.konne', 'p.pieszy', 'z.pociagi', 'r.rejestracja']

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

#         # Do actions based on args
#         if (args.input):
#             self.__OpenLocation(args.input)

    def SetupDefault(self):
        ''' Sets default for UI.'''

    def OpenFile(self, fileEntry):
        ''' Sets default for UI.'''

    def SaveFile(self, fileEntry):
        ''' Sets default for UI.'''

    def Run(self):
        '''  Run gui window thread and return exit code.'''
        self.window.show()
        return self.App.exec_()
