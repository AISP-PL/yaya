"""
Created on 29 gru 2020

@author: spasz
"""

import logging
import os
import shutil
import sys
from copy import copy
from datetime import datetime

from PyQt5 import QtCore
from PyQt5.QtWidgets import (
    QApplication,
    QButtonGroup,
    QFileDialog,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
)

from Detectors.common.Detector import NmsMethod
from Detectors.common.image_strategy import ImageStrategy
from engine.annote import GetClasses
from engine.session import Session
from helpers.files import ChangeExtension, FixPath
from MainWindow_ui import Ui_MainWindow
from ViewerEditorImage import ViewerEditorImage
from views.ViewFilters import ViewFilters
from views.ViewImagesSummary import ViewImagesSummary
from views.ViewImagesTable import ViewImagesTable
from views.ViewImagesTableRow import ViewImagesTableRow


class MainWindowGui(Ui_MainWindow):
    """
    classdocs
    """

    def __init__(
        self,
        args,
        detector,
        annoter,
    ):
        """
        Constructor
        """
        # Session : Start
        self.session = Session()
        # Config
        self.info = {"Callbacks": True}
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
        self.App.setApplicationName("YAYA")
        self.App.setOrganizationName("AISP")
        self.App.setOrganizationDomain("aisp.pl")
        self.ui = Ui_MainWindow()
        self.window = QMainWindow()
        self.ui.setupUi(self.window)

        # System stored user settings (QSettings)
        # --------------------------
        self.system_settings = QtCore.QSettings(self.App)

        # Setup all
        self.SetupCallbacks()
        self.SetupDefault()
        self.Setup()

        # Locations : Open
        last_location = self.OpenedDirectoriesGet(amount=1)

        # Locations : If stored, try to open last location.
        if last_location is not None:
            is_opened = self.LocationOpen(last_location[0])

        # Locations: Open Examples if not stored or open failed.
        if (last_location is None) or (not is_opened):
            self.LocationOpen("input")

    def OpenedDirectoriesStore(self, directory_path: str, limit: int = 64):
        """
        Store opened directory path in system settings.

        Parameters
        ----------
        directory_path : str
            Directory path to store.
        limit : int
            Limit of stored directories.
        """
        # Opened directories : Get
        opened_directories = self.system_settings.value("opened_directories", [])

        # Opened directories : Insert at first position (stack)
        opened_directories.insert(0, directory_path)
        if len(opened_directories) > limit:
            opened_directories.pop()

        # Filter existing
        opened_directories = list(dict.fromkeys(opened_directories))

        # Opened directories : Save
        self.system_settings.setValue("opened_directories", opened_directories)

    def OpenedDirectoriesGet(self, amount: int = 1) -> list:
        """
        Get last opened directory path from system settings.

        Parameters
        ----------
        amount : int
            Amount of directories to return.


        Returns
        -------
        str
        """
        # Opened directories : Get
        opened_directories = self.system_settings.value("opened_directories", [])

        # Check : Empty
        if len(opened_directories) == 0:
            return None

        # Opened directories : Return first
        return opened_directories[0:amount]

    def ImageIDToRowNumber(self, imageID: int):
        """Image number to row index."""
        # Found index
        foundIndex = None

        # Check : Row count == 0
        if self.ui.fileSelectorTableWidget.rowCount() == 0:
            return None

        # Find rowIndex of imageNumber
        for rowIndex in range(self.ui.fileSelectorTableWidget.rowCount()):
            item = self.ui.fileSelectorTableWidget.item(rowIndex, 0)
            if item is None:
                continue

            if int(item.toolTip()) == imageID:
                foundIndex = rowIndex
                break

        return foundIndex

    def RowNumberToImageID(self, rowIndex: int):
        """Row index to image number."""
        # Check : Return 0 if rows == 0
        if self.ui.fileSelectorTableWidget.rowCount() == 0:
            return 0

        # Find rowIndex of imageNumber
        item = self.ui.fileSelectorTableWidget.item(rowIndex, 0)
        if item is not None:
            return int(item.toolTip())

        # Otherwise : Return row zero image number
        item = self.ui.fileSelectorTableWidget.item(0, 0)
        if item is not None:
            return int(item.toolTip())

        return 0

    def SetupCallbacks(self):
        """Setup only once after init."""
        # Image scaling
        self.ui.imageScalingComboBox.currentTextChanged.connect(
            self.CallbackImageScalingTextChanged
        )

        # List of detector labels - Create
        self.ui.labelsListWidget.currentRowChanged.connect(
            self.CallbackLabelsRowChanged
        )

        # Images table : Setup
        self.ui.fileSelectorTableWidget.itemClicked.connect(
            self.CallbackFileSelectorItemClicked
        )

        # Detector : Callbacks for sliders, method
        self.ui.detectorConfidenceSlider.valueChanged.connect(
            self.CallbackDetectorUpdate
        )
        self.ui.detectorNmsSlider.valueChanged.connect(self.CallbackDetectorUpdate)
        self.ui.detectorNmsCombo.currentTextChanged.connect(self.CallbackDetectorUpdate)

        # Paint size slider
        self.ui.paintSizeSlider.valueChanged.connect(self.CallbackPaintSizeSlider)

        # Menu handling
        self.ui.actionZamknijProgram.triggered.connect(self.CallbackClose)
        self.ui.actionZapisz.triggered.connect(self.CallbackSaveFileAnnotationsButton)
        self.ui.actionOtworzLokacje.triggered.connect(self.CallbackOpenLocation)
        self.ui.actionSave_screenshoot.triggered.connect(self.CallbackScreenshot)
        self.ui.actionSave_copy.triggered.connect(self.CallbackSaveCopy)

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
            self.CallbackSaveFileAnnotationsButton
        )
        self.ui.DeleteImageAnnotationsButton.clicked.connect(
            self.CallbackDeleteImageAnnotationsButton
        )
        self.ui.DeleteNotAnnotatedFilesButton.clicked.connect(
            self.CallbackDeleteNotAnnotatedFilesButton
        )
        self.ui.CacheImageButton.clicked.connect(
            lambda _x: self.session.fileentry_store(self.annoter.GetFile())
        )

        # Buttons - Annotations
        self.ui.addAnnotationsButton.clicked.connect(self.CallbackAddAnnotationsButton)
        self.ui.renameAnnotationsButton.clicked.connect(
            self.CallbackRenameAnnotationsButton
        )
        self.ui.removeAnnotationsButton.clicked.connect(
            self.CallbackRemoveAnnotationsButton
        )
        self.ui.detectAnnotationsButton.clicked.connect(self.CallbackDetectAnnotations)
        self.ui.hideLabelsButton.clicked.connect(self.CallbackHideLabelsButton)
        self.ui.hideAnnotationsButton.clicked.connect(
            self.CallbackHideAnnotationsButton
        )
        self.ui.ClearAnnotationsButton.clicked.connect(
            self.CallbackClearAnnotationsButton
        )

        # Buttons - Painting
        self.ui.paintCircleButton.clicked.connect(self.CallbackPaintCircleButton)

        # Buttons : Filters
        self.ui.annotationFilterButton.clicked.connect(
            self.CallbackAnnotationsFilterButton
        )
        self.ui.detFilterButton.clicked.connect(self.CallbackDetectionsFilterButton)

        # Buttons - list of gui key codes
        self.ui.button1.clicked.connect(
            lambda: self.CallbackKeycodeButtonClicked(self.ui.button1)
        )
        self.ui.button2.clicked.connect(
            lambda: self.CallbackKeycodeButtonClicked(self.ui.button2)
        )
        self.ui.button3.clicked.connect(
            lambda: self.CallbackKeycodeButtonClicked(self.ui.button3)
        )
        self.ui.button4.clicked.connect(
            lambda: self.CallbackKeycodeButtonClicked(self.ui.button4)
        )
        self.ui.button5.clicked.connect(
            lambda: self.CallbackKeycodeButtonClicked(self.ui.button5)
        )
        self.ui.button6.clicked.connect(
            lambda: self.CallbackKeycodeButtonClicked(self.ui.button6)
        )
        self.ui.button7.clicked.connect(
            lambda: self.CallbackKeycodeButtonClicked(self.ui.button7)
        )
        self.ui.button8.clicked.connect(
            lambda: self.CallbackKeycodeButtonClicked(self.ui.button8)
        )
        self.ui.button9.clicked.connect(
            lambda: self.CallbackKeycodeButtonClicked(self.ui.button9)
        )
        self.ui.button10.clicked.connect(
            lambda: self.CallbackKeycodeButtonClicked(self.ui.button10)
        )
        self.ui.button11.clicked.connect(
            lambda: self.CallbackKeycodeButtonClicked(self.ui.button11)
        )
        self.ui.button12.clicked.connect(
            lambda: self.CallbackKeycodeButtonClicked(self.ui.button12)
        )
        self.ui.buttonOffset.clicked.connect(self.CallbackKeycodeOffsetButtonClicked)

    def SetupDefault(self):
        """Sets default for UI."""
        # Annoter - process first time.
        self.annoter.Process()

        # List of detector labels - Create
        self.ui.labelsListWidget.clear()
        for index, className in enumerate(GetClasses()):
            self.ui.labelsListWidget.addItem(
                QListWidgetItem(f"{index} : {className}", self.ui.labelsListWidget)
            )
        self.ui.labelsListWidget.setCurrentRow(0)

        # Detector : Confidence and NMS sliders defaults (0.5 and 0.45)
        self.ui.detectorConfidenceSlider.setValue(round(self.annoter.confidence * 100))
        self.ui.detectorNmsSlider.setValue(round(self.annoter.nms * 100))
        self.ui.detectorNmsCombo.clear()
        for method in NmsMethod:
            self.ui.detectorNmsCombo.addItem(method.name)
        self.CallbackDetectorUpdate()

        # Detctor : Image Strategy combobox
        self.ui.imageStrategyCombo.clear()
        for strategy in ImageStrategy:
            self.ui.imageStrategyCombo.addItem(strategy.value)

        # Filters classes : Setup
        labels = GetClasses()
        ViewFilters.ViewClasses(
            self.ui.annotationsFilterGrid,
            layout_title="Filter of annotations",
            button_ids=labels,
            button_labels=labels,
            button_callback=self.CallbackFilterClassesClicked,
            buttons_group=ViewFilters.filter_classes_group,
        )
        # Filters detections : Setup
        ViewFilters.ViewClasses(
            self.ui.detectionsFilterGrid,
            layout_title="Filter of detections",
            button_ids=labels,
            button_labels=labels,
            button_callback=self.CallbackFilterClassesClicked,
            buttons_group=ViewFilters.filter_detections_group,
        )

        # Files : Get
        files = self.annoter.GetFiles(
            filter_annotations_classnames=self.FilterClassesGet(),
            filter_detections_classnames=self.FilterDetectionClassesGet(),
        )

        # Images table : Setup
        ViewImagesTable.View(self.ui.fileSelectorTableWidget, files)

        # Images summary : Setup
        ViewImagesSummary.View(self.ui.fileSummaryLabel, files)

    def Setup(self, table_refresh: bool = False):
        """Setup again UI."""
        filename = self.annoter.GetFilename()
        imageWidth, imageHeight, imageBytes = self.annoter.GetImageSize()
        imageNumber = self.annoter.GetFileIndex()
        imageID = self.annoter.GetFileID()
        imageCount = self.annoter.GetFilesCount()
        imageAnnotatedCount = self.annoter.GetFilesAnnotatedCount()

        # Setup progress bar
        self.ui.progressBar.setMinimum(0)
        self.ui.progressBar.setMaximum(imageCount)
        self.ui.progressBar.setFormat(
            f"Completed {imageAnnotatedCount}/{imageCount} %p%"
        )
        self.ui.progressBar.setValue(imageAnnotatedCount)

        # Setup horizontal file slider
        self.ui.fileNumberSliderLabel.setText(
            "ID%u (%u/%u)" % (imageID, imageNumber, imageCount)
        )

        # Setup file info
        self.ui.fileLabel.setText(
            f"[{imageWidth}px x {imageHeight}x x {imageBytes}B] {imageID}/{filename}"
            + f" | Annotations: {self.annoter.annotations_count}"
        )

        # Setup files selector table widget
        fileEntry = self.annoter.GetFile()

        # Find rowIndex of imageNumber
        rowIndex = self.ImageIDToRowNumber(imageID)

        if (fileEntry is not None) and (rowIndex is not None):
            self.ui.fileSelectorTableWidget.setSortingEnabled(False)
            ViewImagesTableRow.View(
                self.ui.fileSelectorTableWidget, rowIndex, fileEntry, isSelected=True
            )
            self.ui.fileSelectorTableWidget.setSortingEnabled(True)

        # Paint size slider
        self.ui.paintLabel.setText("Paint size %u" % self.ui.paintSizeSlider.value())

        # Setup errors tick
        self.annoter.GetErrors()
        # @TODO

        # Setup viewer/editor
        self.ui.viewerEditor.SetAnnoter(self.annoter)
        self.ui.viewerEditor.SetImage(self.annoter.GetImage())

        # Table : Refresh
        if table_refresh:
            files = self.annoter.GetFiles(
                filter_annotations_classnames=self.FilterClassesGet(),
                filter_detections_classnames=self.FilterDetectionClassesGet(),
            )

            # Images table : Setup
            ViewImagesTable.View(self.ui.fileSelectorTableWidget, files)

            # Images summary : Setup
            ViewImagesSummary.View(self.ui.fileSummaryLabel, files)

    def Run(self):
        """Run gui window thread and return exit code."""
        self.window.show()
        return self.App.exec_()

    def FilterClassesGet(self) -> list[str]:
        """Get classes filter from every button from
        self.ui.filtersGrid
        """
        if ViewFilters.filter_classes_group is None:
            return []

        # Get all checked buttons
        checked = [
            button.text()
            for button in ViewFilters.filter_classes_group.buttons()
            if button.isChecked()
        ]

        return checked

    def FilterDetectionClassesGet(self) -> list[str]:
        """Get classes filter from every button from
        self.ui.filtersGrid
        """
        if ViewFilters.filter_detections_group is None:
            return []

        # Get all checked buttons
        checked = [
            button.text()
            for button in ViewFilters.filter_detections_group.buttons()
            if button.isChecked()
        ]

        return checked

    def CallbackFilterClassesClicked(self, label: str):
        """Callback for filter classes button clicked."""
        self.Setup(table_refresh=True)

    def CallbackImageScalingTextChanged(self, text):
        """Callback when image scaling text changed."""
        if text == "Resize":
            self.ui.viewerEditor.SetImageScaling(ViewerEditorImage.ImageScalingResize)
        elif text == "ResizeAspectRatio":
            self.ui.viewerEditor.SetImageScaling(
                ViewerEditorImage.ImageScalingResizeAspectRatio
            )
        elif text == "OriginalSize":
            self.ui.viewerEditor.SetImageScaling(
                ViewerEditorImage.ImageScalingOriginalSize
            )
        else:
            logging.error("(MainWindow) Unknown value!")

    def CallbackKeycodeOffsetButtonClicked(self):
        """Callback when keycode offset button clicked."""
        self.keysOffset += self.keysSize
        if self.keysOffset >= self.ui.labelsListWidget.count():
            self.keysOffset = 0
        # Call like button 1 clicked
        self.CallbackKeycodeButtonClicked(self.ui.button1)

    def CallbackKeycodeButtonClicked(self, button):
        """Callback when keycode button clicked."""
        indexChr = self.keysOffset + int(button.text()) - 1
        if indexChr >= self.ui.labelsListWidget.count():
            indexChr = self.ui.labelsListWidget.count() - 1

        self.ui.labelsListWidget.setCurrentRow(indexChr)

    def CallbackLabelsRowChanged(self, index):
        """Current labels row changed."""
        self.ui.viewerEditor.SetClassNumber(index)

    def CallbackFileSelectorItemClicked(self, item):
        """When file selector item was clicked."""
        # Read current file number
        fileID = int(item.toolTip())
        # Update annoter
        self.annoter.SetImageID(fileID)
        # Setup UI again
        self.Setup()

    def CallbackPaintSizeSlider(self):
        """Paint size slider changed."""
        self.ui.viewerEditor.SetEditorModeArgument(self.ui.paintSizeSlider.value())
        self.Setup()

    def CallbackPaintCircleButton(self):
        """Paint circle button."""
        self.ui.toolSettingsStackedWidget.setCurrentWidget(self.ui.pageCircle)
        self.ui.viewerEditor.SetEditorMode(
            ViewerEditorImage.ModePaintCircle, argument=self.ui.paintSizeSlider.value()
        )

    def CallbackDetectAnnotations(self):
        """Detect annotations."""
        self.ui.toolSettingsStackedWidget.setCurrentWidget(self.ui.pageDetector)

        self.annoter.confidence = self.ui.detectorConfidenceSlider.value() / 100
        self.annoter.nms = self.ui.detectorNmsSlider.value() / 100
        self.annoter.nmsMethod = NmsMethod(self.ui.detectorNmsCombo.currentText())
        self.annoter.imageStrategy = ImageStrategy(
            self.ui.imageStrategyCombo.currentText()
        )
        self.annoter.Process(forceDetector=True)
        self.Setup()

    def CallbackDetectorUpdate(self):
        """Detector update."""

        self.ui.detectorDetails.setText(self.annoter.detector.details_str)
        self.ui.detectorConfidenceLabel.setText(
            f"Confidence: {self.ui.detectorConfidenceSlider.value()/100:02}%"
        )
        self.ui.detectorNmsLabel.setText(
            f"NMS: {self.ui.detectorNmsSlider.value()/100:02}%"
        )

    def CallbackAddAnnotationsButton(self):
        """Remove annotations."""
        self.ui.toolSettingsStackedWidget.setCurrentWidget(self.ui.pageAnnotations)
        self.ui.viewerEditor.SetEditorMode(ViewerEditorImage.ModeAddAnnotation)

    def CallbackRenameAnnotationsButton(self):
        """Remove annotations."""
        self.ui.toolSettingsStackedWidget.setCurrentWidget(self.ui.pageAnnotations)
        self.ui.viewerEditor.SetEditorMode(ViewerEditorImage.ModeRenameAnnotation)

    def CallbackRemoveAnnotationsButton(self):
        """Remove annotations."""
        self.ui.toolSettingsStackedWidget.setCurrentWidget(self.ui.pageAnnotations)
        self.ui.viewerEditor.SetEditorMode(ViewerEditorImage.ModeRemoveAnnotation)

    def CallbackHideLabelsButton(self):
        """Callback"""
        self.ui.viewerEditor.SetOption(
            "isLabelsHidden", not self.ui.viewerEditor.GetOption("isLabelsHidden")
        )

    def CallbackHideAnnotationsButton(self):
        """Callback"""
        self.ui.viewerEditor.SetOption(
            "isAnnotationsHidden",
            not self.ui.viewerEditor.GetOption("isAnnotationsHidden"),
        )

    def CallbackSaveFileAnnotationsButton(self):
        """Callback"""
        self.annoter.Save()
        self.Setup()

    def CallbackClearAnnotationsButton(self):
        """Callback"""
        self.annoter.ClearAnnotations()
        self.Setup()

    def CallbackAnnotationsFilterButton(self):
        """Remove annotations."""
        self.ui.toolSettingsStackedWidget.setCurrentWidget(self.ui.pageAnnFilter)
        # self.ui.viewerEditor.SetEditorMode(ViewerEditorImage.ModeRenameAnnotation)

    def CallbackDetectionsFilterButton(self):
        """Remove annotations."""
        self.ui.toolSettingsStackedWidget.setCurrentWidget(self.ui.pageDetFilter)
        # self.ui.viewerEditor.SetEditorMode(ViewerEditorImage.ModeRenameAnnotation)

    def CallbackDeleteImageAnnotationsButton(self):
        """Callback"""
        # Remove QtableWidget row
        rowIndex = self.ImageIDToRowNumber(self.annoter.GetFileID())
        if rowIndex is not None:
            self.ui.fileSelectorTableWidget.removeRow(rowIndex)
            # Remove annoter data
            self.annoter.Delete()
            self.annoter.Process()
            self.Setup()

    def CallbackDeleteNotAnnotatedFilesButton(self):
        """Callback."""
        button_reply = QMessageBox.question(
            self.window,
            "Delete all not annotated images",
            "Are you sure (delete not annotated) ?",
        )
        if button_reply == QMessageBox.Yes:
            filesList = copy(self.annoter.GetFiles())
            for fileEntry in filesList:
                if fileEntry["IsAnnotation"] is False:
                    self.annoter.Delete(fileEntry)

    def CallbackNextFile(self):
        """Callback"""
        image_id = self.annoter.GetFileID()
        # Next table row : From image_id
        table_row = self.ImageIDToRowNumber(image_id) + 1
        if table_row >= self.ui.fileSelectorTableWidget.rowCount():
            table_row = 0
        # Next image_id : From table row
        next_image_id = self.RowNumberToImageID(table_row)

        self.annoter.SetImageID(next_image_id)
        self.Setup()

    def CallbackPrevFile(self):
        """Callback"""
        image_id = self.annoter.GetFileID()
        # Previous table row : From image_id
        table_row = self.ImageIDToRowNumber(image_id) - 1
        if table_row < 0:
            table_row = self.ui.fileSelectorTableWidget.rowCount() - 1
        # Previous image_id : From table row
        prev_image_id = self.RowNumberToImageID(table_row)

        self.annoter.SetImageID(prev_image_id)
        self.Setup()

    def CallbackOpenLocation(self):
        """Open location callback."""
        # Open file dialog
        filepath = QFileDialog.getExistingDirectory(None, "Select Directory")

        # Open location
        self.LocationOpen(filepath)

    def LocationOpen(self, filepath: str) -> bool:
        """
        Open location and process files.

        Parameters
        ----------
        filepath : str
            Filepath to open.
        """

        # Check : Not None or empty
        if (filepath is None) or (len(filepath) == 0):
            return False

        # System settings : Store filepaths
        self.OpenedDirectoriesStore(filepath)

        self.annoter.OpenLocation(FixPath(filepath))
        self.SetupDefault()
        self.Setup()
        return True

    def CallbackClose(self):
        """Close GUI callback."""
        logging.debug("Closing application!")
        self.window.close()

    def CallbackScreenshot(self):
        """Save configuration."""
        file = self.annoter.GetFile()

        if file is not None:
            # Set default screenshots location
            """TODO fix windows and linux hanling of this code."""
            if os.name == "posix":
                screenshotsPath = "/home/%s/Obrazy/" % (os.environ.get("USER", "Error"))
            else:
                screenshotsPath = "C:\\"
            # Set screenshot filename
            screenshotFilename = file["Name"] + datetime.now().strftime(
                "%Y%d%m-%H%M%S.png"
            )
            # Call ui save
            result = self.ui.viewerEditor.ScreenshotToFile(
                screenshotsPath + screenshotFilename
            )

            if result is None:
                logging.error("Screenshot error!")

    def CallbackSaveCopy(self):
        """Save configuration."""
        file = self.annoter.GetFile()

        if file is not None:
            # Set default screenshots location
            if os.name == "posix":
                screenshotsPath = "/home/%s/Obrazy/" % (os.environ.get("USER", "Error"))
            else:
                screenshotsPath = "C:\\"

            # Copy original image file to screenshots path
            shutil.copy(file["Path"], screenshotsPath + file["Name"])

            # Copy annotations .txt file to screenshots path
            annotationsPath = ChangeExtension(file["Path"], ".txt")
            if os.path.exists(annotationsPath):
                shutil.copy(
                    annotationsPath,
                    screenshotsPath + ChangeExtension(file["Name"], ".txt"),
                )
