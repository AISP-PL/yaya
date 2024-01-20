'''
Created on 29 gru 2020

@author: spasz
'''
import shutil
import sys
import os
import logging
from Detectors.common.Detector import NmsMethod
from Ui_MainWindow import Ui_MainWindow
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QTableWidgetItem,\
    QListWidgetItem, QButtonGroup, QMessageBox
from PyQt5 import QtCore, QtGui
from engine.annote import GetClasses
from ViewerEditorImage import ViewerEditorImage
from helpers.files import ChangeExtension, FixPath
from copy import copy
from PyQt5.QtCore import Qt
from datetime import datetime
from views.ViewImagesSummary import ViewImagesSummary
from views.ViewImagesTable import ViewImagesTable
from views.ViewImagesTableRow import ViewImagesTableRow


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
        self.SetupCallbacks()
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

    def SetupCallbacks(self):
        ''' Setup only once after init.'''
        # Image scaling
        self.ui.imageScalingComboBox.currentTextChanged.connect(
            self.CallbackImageScalingTextChanged)
        
        # List of detector labels - Create
        self.ui.labelsListWidget.currentRowChanged.connect(
            self.CallbackLabelsRowChanged)
        
        # Images table : Setup
        self.ui.fileSelectorTableWidget.itemClicked.connect(
            self.CallbackFileSelectorItemClicked)

        # Detector : Callbacks for sliders, method
        self.ui.detectorConfidenceSlider.valueChanged.connect(
            self.CallbackDetectorUpdate)
        self.ui.detectorNmsSlider.valueChanged.connect(
            self.CallbackDetectorUpdate)
        self.ui.detectorNmsCombo.currentTextChanged.connect(
            self.CallbackDetectorUpdate)

        # Paint size slider
        self.ui.paintSizeSlider.valueChanged.connect(
            self.CallbackPaintSizeSlider)

        # Menu handling
        self.ui.actionZamknijProgram.triggered.connect(self.CallbackClose)
        self.ui.actionZapisz.triggered.connect(
            self.CallbackSaveFileAnnotationsButton)
        self.ui.actionOtworzLokacje.triggered.connect(
            self.CallbackOpenLocation)
        self.ui.actionSave_screenshoot.triggered.connect(
            self.CallbackScreenshot)
        self.ui.actionSave_copy.triggered.connect(
            self.CallbackSaveCopy)
        
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
        self.ui.hideLabelsButton.clicked.connect(
            self.CallbackHideLabelsButton)
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

    def SetupDefault(self):
        ''' Sets default for UI.'''
        # Annoter - process first time.
        self.annoter.Process()

        # List of detector labels - Create
        self.ui.labelsListWidget.clear()
        for index, className in enumerate(GetClasses()):
            self.ui.labelsListWidget.addItem(QListWidgetItem(f"{index} : {className}", 
                                                             self.ui.labelsListWidget))
        self.ui.labelsListWidget.setCurrentRow(0)

        # Detector : Confidence and NMS sliders defaults (0.5 and 0.45)
        self.ui.detectorConfidenceSlider.setValue(round(self.annoter.confidence*100))
        self.ui.detectorNmsSlider.setValue(round(self.annoter.nms*100))
        self.ui.detectorNmsCombo.clear()
        for method in NmsMethod:
            self.ui.detectorNmsCombo.addItem(method.name)
        self.CallbackDetectorUpdate()

        # Images table : Setup
        ViewImagesTable.View(
            self.ui.fileSelectorTableWidget, self.annoter.GetFiles())

        # Images summary : Setup
        ViewImagesSummary.View(self.ui.fileSummaryLabel,
                               self.annoter.GetFiles())



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
        self.ui.fileLabel.setText(
            f'[{imageWidth}px x {imageHeight}x x {imageBytes}B] {imageID}/{filename} | Annotations: {self.annoter.annotations_count}')

        # Setup files selector table widget
        fileEntry = self.annoter.GetFile()

        # Find rowIndex of imageNumber
        rowIndex = self.ImageIDToRowNumber(imageID)

        if (fileEntry is not None):
            self.ui.fileSelectorTableWidget.setSortingEnabled(False)
            ViewImagesTableRow.View(self.ui.fileSelectorTableWidget,
                                    rowIndex,
                                    fileEntry)
            self.ui.fileSelectorTableWidget.setSortingEnabled(True)

#         # Setup files selector table widget
#         self.ui.fileSelectorTableWidget.clearSelection()
#         if (imageCount != 0):
#             # Select whole row with image
#             for i in range(self.ui.fileSelectorTableWidget.columnCount()):
#                 item = self.ui.fileSelectorTableWidget.item(rowIndex, i)
#                 item.setSelected(True)

# #             Move verticall scroll bar also
# #             self.ui.fileSelectorTableWidget.verticalScrollBar().setValue(rowIndex)

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
        self.ui.toolSettingsStackedWidget.setCurrentWidget(
            self.ui.pageDetector)
        self.annoter.confidence = self.ui.detectorConfidenceSlider.value() / 100
        self.annoter.nms = self.ui.detectorNmsSlider.value() / 100
        self.annoter.nmsMethod = NmsMethod(
            self.ui.detectorNmsCombo.currentText())
        self.annoter.Process(forceDetector=True)
        self.Setup()

    def CallbackDetectorUpdate(self):
        ''' Detector update.'''
        self.ui.detectorConfidenceLabel.setText(
            f'Confidence: {self.ui.detectorConfidenceSlider.value()/100:02}%')
        self.ui.detectorNmsLabel.setText(
            f'NMS: {self.ui.detectorNmsSlider.value()/100:02}%')

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

    def CallbackHideLabelsButton(self):
        '''Callback'''
        self.ui.viewerEditor.SetOption('isLabelsHidden',
                                       not self.ui.viewerEditor.GetOption('isLabelsHidden'))

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
        # Open file dialog
        filepath = QFileDialog.getExistingDirectory(None, 'Select Directory')

        # Check : Not None or empty 
        if (filepath is None) or (len(filepath) == 0):
            return

        self.annoter.OpenLocation(FixPath(filepath))
        self.SetupDefault()
        self.Setup()

    def CallbackClose(self):
        ''' Close GUI callback.'''
        logging.debug('Closing application!')
        self.window.close()

    def CallbackScreenshot(self):
        ''' Save configuration.'''
        file = self.annoter.GetFile()

        if (file is not None):
            # Set default screenshots location
            ''' TODO fix windows and linux hanling of this code. '''
            if (os.name == 'posix'):
                screenshotsPath = '/home/%s/Obrazy/' % (
                    os.environ.get('USER', 'Error'))
            else:
                screenshotsPath = 'C:\\'
            # Set screenshot filename
            screenshotFilename = file['Name'] + \
                datetime.now().strftime('%Y%d%m-%H%M%S.png')
            # Call ui save
            result = self.ui.viewerEditor.ScreenshotToFile(
                screenshotsPath+screenshotFilename)

            if (result is None):
                logging.error('Screenshot error!')

    def CallbackSaveCopy(self):
        ''' Save configuration.'''
        file = self.annoter.GetFile()

        if (file is not None):
            # Set default screenshots location
            if (os.name == 'posix'):
                screenshotsPath = '/home/%s/Obrazy/' % (
                    os.environ.get('USER', 'Error'))
            else:
                screenshotsPath = 'C:\\'

            # Copy original image file to screenshots path
            shutil.copy(file['Path'],
                        screenshotsPath+file['Name'])

            # Copy annotations .txt file to screenshots path
            annotationsPath = ChangeExtension(file['Path'], '.txt')
            if (os.path.exists(annotationsPath)):
                shutil.copy(annotationsPath,
                            screenshotsPath+ChangeExtension(file['Name'], '.txt'))
