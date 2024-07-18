"""
Created on 17 lis 2020

@author: spasz
"""

import logging
import os
from enum import Enum
from math import sqrt
from typing import Optional

import cv2
import numpy as np
from tqdm import tqdm

import engine.annote as annote
from engine.dataset import Dataset
import helpers.boxes as boxes
import helpers.prefilters as prefilters
import helpers.transformations as transformations
from Detectors.common.Detector import NmsMethod
from Detectors.common.image_strategy import ImageStrategy
from Detectors.DetectorYoloWorld import DetectorYOLOWorld
from helpers.files import (
    DeleteFile,
    FixPath,
    GetExtension,
    GetFilename,
    GetNotExistingSha1Filepath,
    IsImageFile,
)
from helpers.metrics import EvaluateMetrics, Metrics
from helpers.textAnnotations import (
    DeleteAnnotations,
    IsExistsAnnotations,
    ReadAnnotations,
    ReadDetections,
    SaveAnnotations,
    SaveDetections,
)
from helpers.visuals import Visuals, VisualsDuplicates


class DetectorSelected(str, Enum):
    """Selected detector."""

    Default = "Default"
    YoloWorld = "YoloWorld"


class Annoter:
    """
    classdocs
    """

    # Sort methods
    NoSort = 0
    SortByDatetime = 1
    SortByInvDatetime = 2
    SortByAlphabet = 3

    def __init__(
        self,
        filepath,
        detector,
        noDetector=False,
        sortMethod=SortByInvDatetime,
        isOnlyNewFiles=False,
        isOnlyOldFiles=False,
        isOnlyErrorFiles=False,
        isOnlyDetectedClass=None,
        isOnlySpecificClass=None,
        forceDetector=False,
        detectorConfidence: float = 0.4,
        detectorNms: float = 0.45,
    ):
        """
        Constructor
        """
        # Set configuration
        self.config = {
            "sortMethod": sortMethod,
            "forceDetector": forceDetector,
            "isOnlyNewFiles": isOnlyNewFiles,
            "isOnlyOldFiles": isOnlyOldFiles,
            "isOnlyErrorFiles": isOnlyErrorFiles,
            "isOnlyDetectedClass": isOnlyDetectedClass,
            "isOnlySpecificClass": isOnlySpecificClass,
        }
        # Yolo World handle
        self.yolo_world = DetectorYOLOWorld()
        self.yolo_world_confidence = 0.1
        self.yolo_world_ontology = {"bus": "g.autobusy"}
        # Path
        self.dirpath = None
        # Detector handle
        self.detector = detector
        self.is_detector_enabled = not noDetector
        # Detector : Confidence value
        self.confidence = detectorConfidence
        # Detector : Image fitting strategy
        self.imageStrategy = ImageStrategy.Rescale
        # Detector : NMS Threshold value
        self.nms = detectorNms
        # Detector : NMS method
        self.nmsMethod = NmsMethod.Nms

        # Selection of detector:
        self.detector_selected = DetectorSelected.Default

        # File entries list
        self.files: Optional[list[dict]] = None
        # Validation dataset
        self.dataset_validation = Dataset()
        # Annotations list
        self.annotations = []
        # Readed image cv2 object
        self.image = None
        # Current file number offset
        self.offset = 0
        # Set of all errors
        self.errors = set()

        # Check : Open location
        if (filepath is not None) and (len(filepath) != 0):
            self.OpenLocation(filepath)

    def __del__(self):
        """Destructor."""
        # filter only images and not excludes
        excludes = [".", "..", "./", ".directory"]
        filenames = os.listdir(self.dirpath)

        # Filter images only
        filenames = [f for f in filenames if (f not in excludes) and (IsImageFile(f))]

        # Get only images with annotations
        filenamesAnnotated = [
            f for f in filenames if (IsExistsAnnotations(self.dirpath + f) is True)
        ]

        # Save results
        datasetPath = FixPath(self.dirpath) + "dataset.txt"
        with open(datasetPath, "w") as f:
            for line in filenamesAnnotated:
                f.write(line + "\n")

            logging.info(
                "(Annoter) Created list of %u/%u annotated images in `%s`.",
                len(filenamesAnnotated),
                len(filenames),
                datasetPath,
            )

    @property
    def detectors_labels(self) -> list[str]:
        """Get prompt labels for detector"""
        return annote.GetClasses() + self.yolo_world.classes

    def GetFileAnnotations(self, filepath):
        """Read file annotations if possible."""
        txtAnnotes = []
        # If exists annotations file
        if IsExistsAnnotations(filepath):
            txtAnnotes = ReadAnnotations(filepath)
            txtAnnotes = [annote.fromTxtAnnote(el) for el in txtAnnotes]

            # Post-check of errors
            self.errors = self.__checkOfErrors()

        return txtAnnotes

    def GetFileImage(self, filepath: str):
        """Read file annotations if possible."""
        if (filepath is None) or (len(filepath) == 0):
            return None

        if not os.path.exists(filepath):
            return None

        try:
            image = cv2.imread(filepath)
            return image
        except Exception as e:
            logging.fatal(
                "(Annoter) CV2 error when readings image `%s`! %s", filepath, e
            )
            return None

    def ReadDetections(self, filepath: str) -> list:
        """Read file annotations if possible."""

        # Selecte extension str
        extension_str = ".detector"
        if self.detector_selected == DetectorSelected.YoloWorld:
            extension_str = ".yoloworld"

        detAnnotes = []
        # If detector annotations not exists then call detector
        if IsExistsAnnotations(filepath, extension=extension_str):
            detAnnotes = ReadDetections(filepath, extension=extension_str)
            detAnnotes = [annote.fromDetection(el) for el in detAnnotes]

        return detAnnotes

    def ProcessDetections(self, im: np.array, filepath: str) -> list:
        """Process detections for file."""

        # Detector : Use Yolo World detector
        if self.detector_selected == DetectorSelected.YoloWorld:
            return self.ProcessYoloWorldDetections(im, filepath)

        # Detector : default detector
        return self.ProcessYolov4Detections(im, filepath)

    def ProcessYolov4Detections(self, im, filepath) -> list:
        """Read file annotations if possible."""
        if (self.detector is None) or (im is None):
            return []

        # Call detector manually!
        detAnnotes = self.detector.Detect(
            im,
            confidence=self.confidence,
            nms_thresh=self.nms,
            boxRelative=True,
            nmsMethod=self.nmsMethod,
            image_strategy=self.imageStrategy,
        )

        # Save/Update detector annotations file
        SaveDetections(filepath, detAnnotes, extension=".detector")

        # Create annotes
        detAnnotes = [annote.fromDetection(el) for el in detAnnotes]
        return detAnnotes

    def ProcessYoloWorldDetections(self, im, filepath) -> list:
        """Read file annotations if possible."""
        if (self.yolo_world is None) or (im is None):
            return []

        self.yolo_world.set_ontology(self.yolo_world_ontology)

        # Call detector manually!
        detAnnotes = self.yolo_world.Detect(
            im,
            confidence=self.yolo_world_confidence,
            nms_thresh=self.nms,
            boxRelative=True,
            nmsMethod=self.nmsMethod,
            image_strategy=self.imageStrategy,
        )

        # Save/Update detector annotations file
        SaveDetections(filepath, detAnnotes, extension=".yoloworld")

        # Create annotes
        detAnnotes = [annote.fromDetection(el) for el in detAnnotes]
        return detAnnotes

    def CalculateYoloMetrics(self, txtAnnotes: list, detAnnotes: list) -> Metrics:
        """Calculate mAP between two annotations sets."""
        metrics = Metrics()
        if len(txtAnnotes):
            metrics = EvaluateMetrics(txtAnnotes, detAnnotes)

        return metrics

    def OpenLocation(self, path: str, force_detector: bool = False):
        """Open images/annotations location."""
        # Check : If path is valid
        if (path is None) or (len(path) == 0):
            logging.error("(Annoter) Path `%s` not exists!", path)
            return

        # Check : If path exists
        if not os.path.exists(path):
            logging.error("(Annoter) Path `%s` not exists!", path)
            return

        # Check : Path is same
        if self.dirpath == path:
            logging.info("(Annoter) Path `%s` is same!", path)
            return

        # Force detector : Update from config
        if force_detector is False:
            force_detector = self.config["forceDetector"]

        # Update dirpath
        self.dirpath = path
        # filter only images and not excludes
        excludes = [".", "..", "./", ".directory"]

        if not os.path.exists(path):
            logging.error("(Annoter) Path `%s` not exists!", path)
            return

        # Fiels : List all directory files and exclude not needed.
        filesToParse = [
            filename
            for filename in os.listdir(path)
            if (filename not in excludes) and (IsImageFile(filename))
        ]

        # Dataset Validation : Read from filepath
        self.dataset_validation.load(FixPath(self.dirpath) + "validation.txt")

        # VisualsDuplicates : Create to find duplicates
        visualsDuplicates = VisualsDuplicates()
        # Files : List of all files
        self.files = []
        # Processing all files
        # startTime = time.time()
        for index, filename in enumerate(
            tqdm(filesToParse, desc="Processing files", unit="files")
        ):
            # Check if annotations exists
            isAnnotation = IsExistsAnnotations(path + filename)

            # Read annotations
            txtAnnotations = self.GetFileAnnotations(path + filename)

            # Force detector if needed
            detections = []
            # Force detector to process every image
            if force_detector is True:
                im = self.GetFileImage(path + filename)
                detections = self.ProcessDetections(im, path + filename)

            # Read historical detections
            else:
                detections = self.ReadDetections(path + filename)

            # For calculation : Filter detections with itself for multiple detections catches.
            detections = prefilters.filter_iou_by_confidence(detections, detections)

            # For view : Filter by IOU internal with same annotes and also with txt annotes.
            detections_filtered = prefilters.filter_iou_by_confidence(
                detections, detections + txtAnnotations
            )

            # Calculate metrics
            metrics = self.CalculateYoloMetrics(txtAnnotations, detections)
            # Calculate visuals
            visuals = Visuals.LoadCreate(
                path + filename, force=self.config["forceDetector"]
            )
            # Visuals : Check dhash is in duplicates
            visuals.isDuplicate = visualsDuplicates.IsDuplicate(visuals)
            # VisualsDuplicates : Update set of image hashes
            visualsDuplicates.Add(visuals)

            # Add file entry
            self.files.append(
                {
                    "Name": filename,
                    "Path": path + filename,
                    "ID": index,
                    "IsAnnotation": isAnnotation,
                    "IsValidation": self.dataset_validation.is_inside(filename),
                    "Annotations": txtAnnotations,
                    "AnnotationsClasses": ", ".join(
                        {f"{item.class_abbrev}" for item in txtAnnotations}
                    ),
                    "Datetime": os.lstat(path + filename).st_mtime,
                    "Errors": len(self.errors),
                    "Detections": detections_filtered,
                    "Detections_original": detections,
                    "Metrics": metrics,
                    "Visuals": visuals,
                }
            )

        # ------- Sorting ------------
        # Sorting : by datetime
        if self.config["sortMethod"] == self.SortByDatetime:
            self.files = sorted(self.files, key=lambda i: i["Datetime"])
        elif self.config["sortMethod"] == self.SortByInvDatetime:
            self.files = sorted(self.files, key=lambda i: -i["Datetime"])
        # Sorting : by alphabet
        elif self.config["sortMethod"] == self.SortByAlphabet:
            self.files = sorted(self.files, key=lambda i: i["Name"])

        # ------- Filtering  ------------
        # Use only not annotated files
        if self.config["isOnlyNewFiles"] is True:
            newFiles = []
            for offset, fileEntry in enumerate(self.files):
                if not fileEntry["IsAnnotation"]:
                    newFiles.append(fileEntry)

            self.files = newFiles

        # Use only files with errors
        if self.config["isOnlyErrorFiles"] is True:
            filesWithErrors = []
            for index, fileEntry in enumerate(self.files):
                if fileEntry["Errors"] != 0:
                    filesWithErrors.append(fileEntry)

            # Swap with files
            self.files = filesWithErrors

        # Use only files with specific class
        if self.config["isOnlySpecificClass"] is not None:
            filesForClass = []
            for offset, fileEntry in enumerate(self.files):
                annotations = self.AnnotationsSelectClasses(
                    fileEntry["Annotations"], [self.config["isOnlySpecificClass"]]
                )
                if (annotations is not None) and (len(annotations) != 0):
                    filesForClass.append(fileEntry)

            self.files = filesForClass

        # Reset values at the end
        self.annotations = []
        self.image = None
        self.offset = 0
        self.errors = set()

    def GetFile(self):
        """Returns current filepath."""
        if (self.files is None) or (len(self.files) == 0):
            return None

        return self.files[self.offset]

    def GetFilename(self):
        """Returns current filepath."""
        #  Check if files none or empty
        if (self.files is None) or (len(self.files) == 0):
            return "Not exists!"

        return self.files[self.offset]["Name"]

    def GetFilepath(self):
        """Returns current filepath."""
        return self.files[self.offset]["Path"]

    def GetErrors(self):
        """Returns current errors list."""
        return self.errors

    def GetImage(self):
        """Returns current image."""
        return self.image

    def GetImageSize(self):
        """Returns current image."""
        if self.image is not None:
            h, w, bytes = self.image.shape
            return w, h, bytes

        return 0, 0, 0

    def GetAnnotationsList(self):
        """Returns annotations list"""
        return [GetFilename(f["Name"]) + ".txt" for f in self.files]

    def GetFiles(
        self,
        filter_annotations_classnames: list[str] = None,
        filter_detections_classnames: list[str] = None,
    ):
        """Returns images list"""
        # Check : Empty or none
        if (self.files is None) or (len(self.files) == 0):
            return None

        # Filter : Iterating over all files
        files = []
        for fileEntry in self.files:
            # Filter : Classes of annotations
            if (filter_annotations_classnames is not None) and (
                len(filter_annotations_classnames) > 0
            ):
                annotations = fileEntry["Annotations"]
                if not any(
                    annotation.className in filter_annotations_classnames
                    for annotation in annotations
                ):
                    continue

            # Filter : Classes of detections
            if (filter_detections_classnames is not None) and (
                len(filter_detections_classnames) > 0
            ):
                detections = fileEntry["Detections_original"]
                if not any(
                    annotation.className in filter_detections_classnames
                    for annotation in detections
                ):
                    continue

            files.append(fileEntry)

        return files

    def GetFileID(self):
        """Returns current image ID."""
        # Check if files none or empty
        if (self.files is None) or (len(self.files) == 0):
            return 0

        if self.offset < len(self.files):
            return self.files[self.offset]["ID"]

        return 0

    def GetFileIndex(self):
        """Returns current image number."""
        return self.offset

    def GetFilesCount(self) -> int:
        """Returns count of processed images number."""
        if self.files is None:
            return 0

        return len(self.files)

    def GetFilesAnnotatedCount(self) -> int:
        """Returns count of processed images number."""
        # Check : Files exists
        if (self.files is None) or (len(self.files) == 0):
            return 0

        annotated = sum([int(fileEntry["IsAnnotation"]) for fileEntry in self.files])
        return annotated

    def SetImageID(self, fileID: int):
        """Sets current image number."""
        # index of ID file
        foundIndex = None
        # Find image with these id
        for index, fileEntry in enumerate(self.files):
            if fileEntry["ID"] == fileID:
                foundIndex = index
                break

        if (foundIndex is not None) and (foundIndex) and (foundIndex < len(self.files)):
            self.offset = foundIndex
            self.Process()
            return True

        return False

    def SetImageNumber(self, number):
        """Sets current image number."""
        if (number >= 0) and (number < len(self.files)):
            self.offset = number
            self.Process()
            return True

        return False

    def TransformShape(self, mode="Flip"):
        """Transform image and annotations shape."""
        if mode == "Flip":
            self.image = transformations.Flip(self.image)
            for a in self.annotations:
                a.box = boxes.FlipHorizontally(1, a.box)

        # Store image modification info
        for a in self.annotations:
            a.authorType = annote.AnnoteAuthorType.byHuman
        self.errors.add("ImageModified!")

    def PaintCircles(self, points, radius, color):
        """Paint list of circles Circle on image."""
        for x, y in points:
            self.image = cv2.circle(self.image, (round(x), round(y)), radius, color, -1)
        self.errors.add("ImageModified!")

    def GetAnnotations(self):
        """Returns current annotations."""
        return self.annotations

    @property
    def annotations_count(self) -> int:
        """Returns current annotations."""
        return len(self.annotations)

    @staticmethod
    def AnnotationsSelectClasses(annotations, classes):
        """Returns current annotations."""
        if annotations is not None:
            annotations = [a for a in annotations if (a.classNumber in classes)]

        return annotations

    def GetAnnotationsSelectClasses(self, classes):
        """Returns current annotations."""
        return self.AnnotationsSelectClasses(self.annotations, classes)

    def AddAnnotation(self, box, classNumber):
        """Adds new annotation by human."""
        self.annotations.append(
            annote.Annote(
                box, classNumber=classNumber, authorType=annote.AnnoteAuthorType.byHand
            )
        )
        logging.debug("(Annoter) Added annotation class %u!", classNumber)
        self.errors = self.__checkOfErrors()

    def ClearAnnotations(self):
        """Clear all annotations."""
        self.annotations = []
        self.errors = self.__checkOfErrors()
        logging.debug("(Annoter) Cleared annotations!")

    def ClearDetections(self):
        """Clear only annotations from detector."""
        self.annotations = [
            annotation
            for annotation in self.annotations
            if annotation.authorType != annote.AnnoteAuthorType.byDetector
        ]
        self.errors = self.__checkOfErrors()

    def RemoveAnnotation(self, element):
        """Remove annotation ."""
        if len(self.annotations) != 0:
            self.annotations.remove(element)
            self.errors = self.__checkOfErrors()

    def IsSynchronized(self):
        """Is all annotations synchronized with file."""
        isSynchronized = True
        for element in self.annotations:
            if element.GetAuthorType() != annote.AnnoteAuthorType.byHuman:
                isSynchronized = False
                break

        return isSynchronized

    def __isClearImageSynchronized(self):
        """True if image was modified."""
        result = not ("ImageModified!" in self.errors)
        if result is False:
            self.errors.remove("ImageModified!")
        return result

    def Delete(self, fileEntry=None):
        """Deletes image and annotations."""
        # If not specified fileEntry then use
        # current fileEntry.
        if fileEntry is None:
            # Use current file
            if self.offset < self.GetFilesCount():
                fileEntry = self.files[self.offset]

        # If entry exists then delete it
        if fileEntry is not None:
            self.ClearAnnotations()
            DeleteAnnotations(fileEntry["Path"])
            DeleteFile(fileEntry["Path"])
            self.files.remove(fileEntry)

            # Step back offset
            self.offset = min(self.offset, self.GetFilesCount() - 1)

    def Create(self):
        """Creates new filepath for new image file."""
        filename = self.GetFilename()
        filename, filepath = GetNotExistingSha1Filepath(filename, self.dirpath)
        cv2.imwrite("%s" % (filepath), self.image)
        self.filenames.insert(self.offset, filename)
        logging.info("(Annoter) New image %s created!", filename)

    def AddRemoveValidationDataset(self):
        """Add or remove current file to validation dataset"""
        filename = self.GetFilename()

        if self.dataset_validation.is_inside(filename):
            self.dataset_validation.remove(filename)
        else:
            self.dataset_validation.add(filename)

        # Dataset : Save if needed
        if self.dataset_validation.is_not_saved():
            self.dataset_validation.save()

        # File entry : Update
        self.files[self.offset]["IsValidation"] = self.dataset_validation.is_inside(
            filename
        )

    def Save(self):
        """Save current annotations."""
        filename = self.GetFilename()

        # If image was modified, then save it also
        if self.__isClearImageSynchronized() is False:
            # Create temporary and original paths
            imgpath = FixPath(self.dirpath) + filename
            tmppath = FixPath(self.dirpath) + "tmp" + GetExtension(filename)
            # Save temporary image
            result = cv2.imwrite(tmppath, self.image)
            if result is False:
                logging.error('(Annoter) Writing image "%s" failed!', imgpath)
                return

            # If saved then atomic move image to original image
            os.system('mv -fv "%s" "%s" ' % (tmppath, imgpath))

        # Check other errors
        self.errors = self.__checkOfErrors()
        if len(self.errors) != 0:
            logging.error("(Annoter) Errors exists in annotations!")
            return

        # Save annotations
        annotations = [annote.toTxtAnnote(el) for el in self.annotations]
        annotations = SaveAnnotations(self.dirpath + filename, annotations)
        logging.debug("(Annoter) Saved annotations for %s!", filename)

        # Dataset : Save if needed
        if self.dataset_validation.is_not_saved():
            self.dataset_validation.save()

        # Process file again after save
        self.Process()

        # Update file entry
        self.files[self.offset]["IsValidation"] = self.dataset_validation.is_inside(
            filename
        )
        self.files[self.offset]["IsAnnotation"] = True
        self.files[self.offset]["Annotations"] = self.annotations
        self.files[self.offset]["AnnotationsClasses"] = ",".join(
            {f"{item.classNumber}" for item in self.annotations}
        )

    def IsEnd(self):
        """True if files ended."""
        return self.offset == self.GetFilesCount()

    def __checkOfErrors(self):
        """Check current image/annotations for errors."""
        errors = set()
        if len(self.annotations) != len(
            prefilters.filter_iou_by_confidence(self.annotations, self.annotations)
        ):
            logging.error("(Annoter) Annotations overrides each other!")
            errors.add("Override error!")

        return errors

    def Process(
        self,
        processImage: bool = True,
        forceDetector: bool = False,
    ):
        """process file."""
        if (self.offset >= 0) and (self.offset < self.GetFilesCount()):
            fileEntry = self.GetFile()

            # Read image
            if processImage is True:
                self.image = im = self.GetFileImage(fileEntry["Path"])

            # All txt annotations
            txtAnnotations = self.GetFileAnnotations(fileEntry["Path"])
            # Detector annotations list
            detAnnotes = []
            # if annotations file not exists or empty then detect.
            if (self.is_detector_enabled is True) and (
                (processImage is True) or (len(txtAnnotations) == 0)
            ):
                # Detector : Process
                detAnnotes = self.ProcessDetections(im, fileEntry["Path"])

                # Calculate metrics
                metrics = self.CalculateYoloMetrics(txtAnnotations, detAnnotes)

                # For view : Filter by IOU internal with same annotes and also with txt annotes.
                if len(txtAnnotations):
                    detAnnotes = prefilters.filter_iou_by_confidence(
                        detAnnotes, detAnnotes + txtAnnotations, maxIOU=sqrt(self.nms)
                    )

                # Store metrics
                fileEntry["Metrics"] = metrics

            # All annotations
            self.annotations = txtAnnotations + detAnnotes

            # Post-check of errors
            self.errors = self.__checkOfErrors()

            return True

        return False

    def ProcessNext(self) -> bool:
        """Process next image."""
        if self.offset < (self.GetFilesCount() - 1):
            self.offset += 1
            self.Process()
            return True

        return False

    def ProcessPrev(self) -> bool:
        """Process next image."""
        if self.offset > 0:
            self.offset -= 1
            self.Process()
            return True

        return False
