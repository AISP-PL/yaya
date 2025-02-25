import logging
import os
import shutil
import sys
from copy import copy
from datetime import datetime

from PyQt5 import QtCore
from PyQt5.QtWidgets import (
    QActionGroup,
    QApplication,
    QButtonGroup,
    QFileDialog,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QTableWidgetItem,
)

from Detectors.common.Detector import NmsMethod
from Detectors.common.image_strategy import ImageStrategy
from engine.annote import GetClasses
from engine.annote_enums import AnnotatorType
from engine.annoter import Annoter, DetectorSelected
from engine.session import Session
from helpers.files import ChangeExtension, FixPath
from MainWindow_ui import Ui_MainWindow
from ViewerEditorImage import ViewerEditorImage
from views.ViewAnnotations import ViewAnnotations
from views.ViewDetections import ViewDetections
from views.ViewFilters import ViewFilters
from views.ViewImagesSummary import ViewImagesSummary
from views.ViewImagesTable import ViewImagesTable


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
        self.annoter: Annoter = annoter
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

        # Location : Open if provided in arguments
        if args.input is not None:
            is_opened = self.LocationOpen(args.input)
            if is_opened:
                return

        # Locations : Get last location
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

    def SetupCallbacks(self) -> None:
        """Setup only once after init."""
        # Image transformations
        self.ui.transform_threshold.clicked.connect(self.callback_transform_threshold)
        self.ui.transform_sharpen.clicked.connect(self.callback_transform_sharpen)
        self.ui.transform_contrast.clicked.connect(self.callback_transform_contrast)
        self.ui.transform_clahe.clicked.connect(self.callback_transform_clahe)

        # List of detector labels - Create
        self.ui.labelsListWidget.currentRowChanged.connect(
            self.CallbackLabelsRowChanged
        )

        # Images table : Setup
        self.ui.fileSelectorTableWidget.itemClicked.connect(
            lambda item: self.CallbackFileSelectorItemClicked(item, from_data=False)
        )

        # Annotations table : Setup
        self.ui.tableAnnotations.itemClicked.connect(
            self.CallbackFileAnnotationSelected
        )

        # Detections table : Setup
        self.ui.tableDetections.itemClicked.connect(self.CallbackFileAnnotationSelected)

        # Detector : Callbacks for sliders, method
        self.ui.detectorConfidenceSlider.valueChanged.connect(
            self.CallbackDetectorUpdate
        )
        self.ui.detectorNmsSlider.valueChanged.connect(self.CallbackDetectorUpdate)
        self.ui.detectorNmsCombo.currentTextChanged.connect(self.CallbackDetectorUpdate)
        self.ui.actionEnable_detector.triggered.connect(self.CallbackDetectorUpdate)

        # Setup : Selection and move of detections and copy and paste

        # YoloWorld
        self.ui.yoloWorldConfidenceSlider.valueChanged.connect(
            self.CallbackYoloWorldUpdate
        )
        self.ui.yoloWorldPrompt.textChanged.connect(self.CallbackYoloWorldUpdate)
        self.ui.yoloWorldButton.clicked.connect(self.CallbackDetectYoloWorld)

        # Paint size slider
        self.ui.paintSizeSlider.valueChanged.connect(self.CallbackPaintSizeSlider)

        # Menu handling
        self.ui.actionZamknijProgram.triggered.connect(self.CallbackClose)
        self.ui.actionZapisz.triggered.connect(self.CallbackSaveFileAnnotationsButton)
        self.ui.actionOtworzLokacje.triggered.connect(self.CallbackOpenLocation)
        self.ui.actionSave_screenshoot.triggered.connect(self.CallbackScreenshot)
        self.ui.actionSave_copy.triggered.connect(self.CallbackSaveCopy)
        self.ui.actionClear_detections.triggered.connect(
            self.CallbackClearDetectionsButton
        )
        self.ui.actionCopy_annotations.triggered.connect(self.CallbackCopyAnnotations)
        self.ui.actionPaste_annotations.triggered.connect(self.CallbackPasteAnnotations)
        self.ui.actionThumbnail.triggered.connect(self.CallbackThumbnailSet)

        # Menu action group of annotations : Create exclusive group
        self.annotatorTypeGroup = QActionGroup(self.window)
        self.annotatorTypeGroup.addAction(self.ui.action_annotations_default)
        self.annotatorTypeGroup.addAction(self.ui.action_annotations_confidence_heat)
        self.annotatorTypeGroup.addAction(self.ui.action_annotations_category)
        self.annotatorTypeGroup.setExclusive(True)

        # Menu action group of annotations : callbacks
        self.ui.action_annotations_default.triggered.connect(
            lambda: self.ui.viewerEditor.set_annotator_type(AnnotatorType.Default)
        )
        self.ui.action_annotations_confidence_heat.triggered.connect(
            lambda: self.ui.viewerEditor.set_annotator_type(
                AnnotatorType.ConfidenceHeat
            )
        )
        self.ui.action_annotations_category.triggered.connect(
            lambda: self.ui.viewerEditor.set_annotator_type(AnnotatorType.Category)
        )

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
        self.ui.AddRemoveValidationButton.clicked.connect(
            self.CallbackAddRemoveValidationDataset
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
        self.ui.detectionsClearButton.clicked.connect(
            self.CallbackClearDetectionsButton
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
        self.ui.actionEnable_detector.setChecked(self.annoter.is_detector_enabled)
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

        # Filters images : Setup
        labels = GetClasses()
        ViewFilters.ViewImages(
            self.ui.images_filter_grid,
            callback_annotated_only=self.CallbackFilterImagesAnnotated,
            callback_validation_only=self.CallbackFilterImagesValidation,
        )

        # Filters annotations : Setup
        labels = GetClasses()
        ViewFilters.ViewClasses(
            self.ui.annotationsFilterGrid,
            layout_title="Filter of annotations",
            button_ids=labels,
            button_labels=labels,
            button_callback=self.CallbackFilterAnnotationsClicked,
            buttons_group=ViewFilters.filter_classes_group,
        )

        # Filters detections : Setup
        det_labels = self.annoter.detectors_labels
        ViewFilters.ViewClasses(
            self.ui.detectionsFilterGrid,
            layout_title="Filter of detections",
            button_ids=det_labels,
            button_labels=det_labels,
            button_callback=self.CallbackFilterDetectionsClicked,
            buttons_group=ViewFilters.filter_detections_group,
        )

        # # Files : Get
        # files = self.annoter.GetFiles(
        #     filter_annotations_classnames=self.FilterClassesGet(),
        #     filter_detections_classnames=self.FilterDetectionClassesGet(),
        # )

        # # Images table : Setup
        # ViewImagesTable.View(self.ui.fileSelectorTableWidget, files)

        # # Images summary : Setup
        # ViewImagesSummary.View(self.ui.fileSummaryLabel, files)

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
            ViewImagesTable.ViewRow(
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
            filter_annotations = self.filter_annotations_get()
            filter_detections = self.filter_detections_get()
            files = self.annoter.GetFiles(
                filter_annotations_classnames=filter_annotations,
                filter_detections_classnames=filter_detections,
            )

            # Images table : Setup
            ViewImagesTable.View(self.ui.fileSelectorTableWidget, files)

            # Images summary : Setup
            ViewImagesSummary.View(self.ui.fileSummaryLabel, files)

            # Annotations summary : Setup
            ViewAnnotations.View(
                self.ui.tableAnnotations, files, filter_classes=filter_annotations
            )

            # Detections summary : Setup
            ViewDetections.View(
                self.ui.tableDetections, files, filter_classes=filter_detections
            )

    def Run(self):
        """Run gui window thread and return exit code."""
        self.window.show()
        return self.App.exec_()

    def filter_annotations_get(self) -> list[str]:
        """Get classes filter from every button from
        self.ui.filtersGrid
        """
        if ViewFilters.filter_classes_group is None:
            return []

        # Get all checked buttons
        checked = [
            button.toolTip()
            for button in ViewFilters.filter_classes_group.buttons()
            if button.isChecked()
        ]

        return checked

    def filter_detections_get(self) -> list[str]:
        """Get classes filter from every button from
        self.ui.filtersGrid
        """
        if ViewFilters.filter_detections_group is None:
            return []

        # Get all checked buttons
        checked = [
            button.toolTip()
            for button in ViewFilters.filter_detections_group.buttons()
            if button.isChecked()
        ]

        return checked

    def CallbackFilterImagesValidation(self, only_validation: bool) -> None:
        """Callback for filter images button clicked."""
        ViewImagesTable.filter_validation(
            self.ui.fileSelectorTableWidget, only_validation
        )

    def CallbackFilterImagesAnnotated(self, only_annotated: bool) -> None:
        """Callback for filter images button clicked."""
        ViewImagesTable.filter_annotated(
            self.ui.fileSelectorTableWidget, only_annotated
        )

    def CallbackFilterAnnotationsClicked(self, label: str):
        """Callback for filter classes button clicked."""
        filter_annotations = self.filter_annotations_get()
        ViewDetections.filter_classes(self.ui.tableAnnotations, filter_annotations)

    def CallbackFilterDetectionsClicked(self, label: str) -> None:
        """Callback for filter detections button clicked."""
        filter_detections = self.filter_detections_get()
        ViewDetections.filter_classes(self.ui.tableDetections, filter_detections)

    def CallbackImageScalingTextChanged(self, text: str) -> None:
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

    def callback_transform_threshold(self, state: bool) -> None:
        """Callback when transform threshold button clicked."""
        self.ui.viewerEditor.is_threshold = not self.ui.viewerEditor.is_threshold

    def callback_transform_sharpen(self, state: bool) -> None:
        """Callback when transform sharpen button clicked."""
        self.ui.viewerEditor.is_sharpen = not self.ui.viewerEditor.is_sharpen

    def callback_transform_contrast(self, state: bool) -> None:
        """Callback when transform contrast button clicked."""
        self.ui.viewerEditor.is_contrast = not self.ui.viewerEditor.is_contrast

    def callback_transform_clahe(self, state: bool) -> None:
        """Callback when transform clahe button clicked."""
        self.ui.viewerEditor.is_clahe = not self.ui.viewerEditor.is_clahe

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

    def CallbackFileSelectorItemClicked(
        self, item: QTableWidgetItem, from_data: bool = False
    ):
        """When file selector item was clicked."""
        # Read current file number
        if not from_data:
            fileID = int(item.toolTip())
        else:
            fileID = item.data(QtCore.Qt.UserRole)

        # Update annoter
        self.annoter.SetImageID(fileID)
        # Setup UI again
        self.Setup()

    def CallbackFileAnnotationSelected(self, item: QTableWidgetItem):
        """When annotations selector item was clicked."""
        # Check : Item data
        data = item.data(QtCore.Qt.UserRole)
        if data is None:
            return

        file_id, annotation_id = data
        # Update annoter
        self.annoter.SetImageID(fileID=file_id)
        # Setup UI again
        self.Setup()
        # UI Viewer
        self.ui.viewerEditor.annotation_selected_id = annotation_id

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
        self.detector_selected = DetectorSelected.Default
        self.annoter.Process(forceDetector=True)
        self.Setup()

    def CallbackDetectorUpdate(self):
        """Detector update."""
        if self.annoter.detector is None:
            return

        self.annoter.is_detector_enabled = self.ui.actionEnable_detector.isChecked()

        self.ui.detectorDetails.setText(self.annoter.detector.details_str)
        self.ui.detectorConfidenceLabel.setText(
            f"Confidence: {self.ui.detectorConfidenceSlider.value()/100:02}%"
        )
        self.ui.detectorNmsLabel.setText(
            f"NMS: {self.ui.detectorNmsSlider.value()/100:02}%"
        )

    def CallbackDetectYoloWorld(self):
        """Detect annotations."""
        self.ui.toolSettingsStackedWidget.setCurrentWidget(self.ui.pageYoloWorld)

        # Prompt : change to ontology
        prompt = self.ui.yoloWorldPrompt.text()
        items = prompt.split(",")
        ontology = {}
        for item in items:
            items = item.split(":")
            if items[0] == "":
                continue

            ontology[items[0]] = items[-1]

        # Annoter update
        self.annoter.yolo_world_ontology = ontology
        self.annoter.yolo_world_confidence = (
            self.ui.yoloWorldConfidenceSlider.value() / 100
        )
        self.annoter.detector_selected = DetectorSelected.YoloWorld
        self.annoter.Process(forceDetector=True)
        self.Setup()

    def CallbackYoloWorldUpdate(self):
        """YoloWorld update."""
        self.ui.yoloWorldConfidenceLabel.setText(
            f"Confidence: {self.ui.yoloWorldConfidenceSlider.value()/100:02}%"
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

    def CallbackAddRemoveValidationDataset(self):
        """Callback"""
        self.annoter.AddRemoveValidationDataset()
        self.Setup()

    def CallbackClearAnnotationsButton(self):
        """Callback"""
        self.annoter.ClearAnnotations()
        self.Setup()

    def CallbackClearDetectionsButton(self):
        """Callback"""
        self.annoter.ClearDetections()
        self.Setup()

    def CallbackCopyAnnotations(self):
        """Callback"""
        self.annoter.CopyAnnotations()
        self.Setup()

    def CallbackPasteAnnotations(self):
        """Callback"""
        self.annoter.PasteAnnotations()
        self.Setup()

    def CallbackThumbnailSet(self):
        """Set viewer editor thumbnail to check mode of action"""
        self.ui.viewerEditor.isThumbnail = self.ui.actionThumbnail.isChecked()

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
        image_id = self.annoter.GetFileID()
        # Next table row : From image_id
        table_row = self.ImageIDToRowNumber(image_id) + 1
        if table_row >= self.ui.fileSelectorTableWidget.rowCount():
            table_row = 0
        # Next image_id : From table row
        next_image_id = self.RowNumberToImageID(table_row)

        # Remove QtableWidget row
        rowIndex = self.ImageIDToRowNumber(self.annoter.GetFileID())
        if rowIndex is not None:
            self.ui.fileSelectorTableWidget.removeRow(rowIndex)
            # Remove annoter data
            self.annoter.Delete()
            self.annoter.SetImageID(next_image_id)
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

    def CallbackNextFile(self) -> None:
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
        if filepath is None:
            return

        # Dialog Yes/no to confirm if reprocess detector locations files.
        button_reply = QMessageBox.question(
            self.window,
            "Detector reprocess ",
            "Do you want to reprocess all files by curent detector?",
        )

        force_detector = False
        if button_reply == QMessageBox.Yes:
            force_detector = True

        # Open location
        self.LocationOpen(filepath=filepath, force_detector=force_detector)

    def LocationOpen(self, filepath: str, force_detector: bool = False) -> bool:
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

        self.annoter.OpenLocation(FixPath(filepath), force_detector=force_detector)
        self.SetupDefault()
        self.Setup(table_refresh=True)
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
        if file is None:
            return

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
