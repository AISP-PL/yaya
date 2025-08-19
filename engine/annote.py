"""
Created on 17 lis 2020

@author: spasz
"""

import logging

import cv2
import numpy as np

import helpers.boxes as boxes
from engine.annote_enums import AnnoteAuthorType, AnnoteEvaluation
from helpers.colors import blue, green, red, white, yellow

classNames = []


def Init(names):
    """Initalize class names list"""
    global classNames
    classNames = names


def GetClasses():
    """Returns class name"""
    return classNames


def GetClassName(number: int) -> str:
    """Returns class name"""
    if number < len(classNames):
        return classNames[number]
    else:
        return "Invalid_C" + str(number)


def GetClassNumber(name: str) -> int:
    """Retruns class number"""
    if name in classNames:
        return classNames.index(name)

    logging.error("(Annote) Invalid class name %s.", name)
    return 0


def toTxtAnnote(annote):
    """Creates txt annote from object Annote."""
    classNumber = annote.GetClassNumber()
    box = annote.GetBox()
    return (classNumber, box)


def toYoloDetection(annote):
    """Creates YOLOv4 detection from object Annote."""
    className = annote.GetClassName()
    box = annote.GetBox()
    return (className, 100, box)


def fromTxtAnnote(txtAnnote, defaultAuthor=AnnoteAuthorType.byHuman):
    """Creates Annote from txt annote."""
    classNumber, box = txtAnnote
    return Annote(box, classNumber=classNumber, authorType=defaultAuthor)


def fromDetection(detection):
    """Creates Annote from txt annote."""
    className, confidence, box = detection
    return Annote(
        box,
        className=className,
        confidence=confidence,
        authorType=AnnoteAuthorType.byDetector,
    )


class Annote:
    """
    classdocs
    """

    def __init__(
        self,
        box,
        classNumber=None,
        className=None,
        confidence=100.0,
        authorType=AnnoteAuthorType.byHuman,
    ):
        """
        Constructor
        """
        self.box = box
        self.confidence = confidence
        self.authorType = authorType

        # Visual annotation HSV info
        self.hue = 0.0
        self.saturation = 0.0
        self.brightness = 0.0

        # Evaulation metrics
        self.evalution = AnnoteEvaluation.noEvaluation
        self.evaluation_iou = 0.0
        self.evaluation_confidence = 0.0
        # Evaluate detector class id
        self.evaluation_class_id = -1

        assert (className is not None) or (classNumber is not None)
        if classNumber is None:
            self.className = className
            self.classNumber = GetClassNumber(self.className)
        elif className is None:
            self.classNumber = classNumber
            self.className = GetClassName(self.classNumber)
        else:
            self.classNumber = classNumber
            self.className = className

    def __hash__(self) -> int:
        """Hash function for Annote class."""
        return hash((self.classNumber))

    @property
    def evaluation_class_name(self) -> str:
        """Returns evaluation class name."""
        if self.evaluation_class_id >= 0:
            return GetClassName(self.evaluation_class_id)

        return ""

    @property
    def width(self) -> float:
        """Returns width."""
        return self.box[2] - self.box[0]

    @property
    def height(self) -> float:
        """Returns height."""
        return self.box[3] - self.box[1]

    @property
    def area(self) -> float:
        """Returns area."""
        return self.width * self.height

    @property
    def ratio(self) -> float:
        """Returns ratio."""
        if self.height == 0:
            return 0

        return self.width / self.height

    @property
    def class_abbrev(self):
        """Returns class abbrev."""
        # Split text by '.'
        values = self.className.split(".")

        # Max 3 letters from front
        return values[0][:3].upper()

    def update_hsv_from_grid(
        self, grid: np.ndarray, rows: int = 20, cols: int = 20
    ) -> None:
        """Updates HSV values from image tuple9float,float,float] grid 20x20"""
        # Bbox : Unpack
        x1, y1, x2, y2 = self.box
        row1, col1 = max(0, int(20 * y1)), max(0, int(20 * x1))
        row2, col2 = min(rows - 1, int(20 * y2)), min(cols - 1, int(20 * x2))

        # Get grid values
        values = grid[row1 : row2 + 1, col1 : col2 + 1]

        # Check : Empty
        if values.size == 0:
            self.hue = 0.0
            self.saturation = 0.0
            self.brightness = 0.0
            return

        # Calculate average
        self.hue = np.mean(values[:, :, 0])
        self.saturation = np.mean(values[:, :, 1])
        self.brightness = np.mean(values[:, :, 2])

        # Check for NaN :
        if np.isnan(self.hue) or np.isnan(self.saturation) or np.isnan(self.brightness):
            self.brightness = 0.0
            self.saturation = 0.0
            self.hue = 0.0

    def height_px(self, imwidth: float) -> float:
        """Returns height in pixels."""
        return self.height * imwidth

    def width_px(self, imwidth: float) -> float:
        """Returns width in pixels."""
        return self.width * imwidth

    def area_px(self, imwidth: float, imheight: float) -> float:
        """Returns area in pixels."""
        return self.width_px(imwidth) * self.height_px(imheight)

    def xyxy_px(
        self, imwidth: float, imheight: float
    ) -> tuple[float, float, float, float]:
        """Returns xyxy in pixels."""
        x1, y1, x2, y2 = self.box
        return (
            x1 * imwidth,
            y1 * imheight,
            x2 * imwidth,
            y2 * imheight,
        )

    def SetClassNumber(self, number: int) -> None:
        """Returns class number."""
        self.classNumber = number
        self.className = GetClassName(number)

    def SetAuthorType(self, authorType: AnnoteAuthorType) -> None:
        """Returns author type."""
        self.authorType = authorType

    def SetEvalution(
        self,
        evalution: AnnoteEvaluation,
        iou: float,
        confidence: float,
        evaluation_class_id: int = -1,
    ) -> None:
        """Returns author type."""
        self.evalution = evalution
        self.evaluation_iou = iou
        self.evaluation_confidence = confidence
        self.evaluation_class_id = evaluation_class_id

    def GetClassNumber(self) -> int:
        """Returns class number."""
        return self.classNumber

    def GetClassName(self) -> str:
        """Returns class name."""
        return self.className

    def GetBox(self) -> tuple:
        """Returns box."""
        return self.box

    def GetAuthorType(self) -> AnnoteAuthorType:
        """Returns author type."""
        return self.authorType

    def GetConfidence(self) -> float:
        """Returns confidence."""
        return self.confidence

    def Draw(self, image, highlight=False, isConfidence=True):
        """Draw self."""
        h, w = image.shape[0:2]
        x1, y1, x2, y2 = boxes.ToAbsolute(self.box, w, h)

        # Highlighted annotations have thicker border
        thickness = 1
        if highlight is True:
            thickness = 2

        # Annotation
        if self.authorType == AnnoteAuthorType.byHuman:
            if self.evalution in [
                AnnoteEvaluation.noEvaluation,
                AnnoteEvaluation.TruePositiveLabel,
            ]:
                cv2.rectangle(image, (x1, y1), (x2, y2), green, thickness)
            elif self.evalution == AnnoteEvaluation.TruePositive:
                cv2.rectangle(image, (x1, y1), (x2, y2), yellow, thickness)
            elif self.evalution == AnnoteEvaluation.FalseNegative:
                cv2.rectangle(image, (x1, y1), (x2, y2), red, thickness)

        # Detector annotation
        elif self.authorType == AnnoteAuthorType.byDetector:
            cv2.rectangle(image, (x1, y1), (x2, y2), blue, thickness)
            image = cv2.line(image, (x1, y1), (x2, y2), blue, thickness)
            image = cv2.line(image, (x1, y2), (x2, y1), blue, thickness)

        # Human annotation
        elif self.authorType == AnnoteAuthorType.byHand:
            cv2.rectangle(image, (x1, y1), (x2, y2), white, thickness)

        # Text
        label = self.className
        if self.authorType == AnnoteAuthorType.byDetector:
            label = "{}".format(self.className)
            # If confidence drawing enabled
            if isConfidence:
                label += "[{:.2f}]".format(float(self.confidence))
        cv2.putText(
            image, label, (x1 - 1, y2 - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 3
        )
        cv2.putText(
            image,
            label,
            (x1, y2 - 5),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 255, 255),
            1,
        )

    def IsInside(self, point: tuple) -> bool:
        """True if point is inside note box."""
        return boxes.IsInside(point, self.box)
