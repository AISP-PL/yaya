"""
Created on 17 lis 2020

@author: spasz
"""

import logging
from enum import Enum

import cv2
from PyQt5.QtCore import QPoint, Qt

import helpers.boxes as boxes
from helpers.colors import blue, green, red, white, yellow
from helpers.QtDrawing import QDrawRectangle, QDrawText

classNames = []


def Init(names):
    """Initalize class names list"""
    global classNames
    classNames = names


def GetClasses():
    """Returns class name"""
    return classNames


def GetClassName(number):
    """Returns class name"""
    if number < len(classNames):
        return classNames[number]
    else:
        return "Invalid_C" + str(number)


def GetClassNumber(name):
    """Retruns class number"""
    if name in classNames:
        return classNames.index(name)

    logging.error("(Annote) Invalid class name %s.", name)
    return 0


class AnnoteAuthorType(Enum):
    """Annotation author type."""

    byHuman = 0
    byDetector = 1
    byHand = 2


class AnnoteEvaluation(Enum):
    """Annotation evalution."""

    noEvaluation = 0
    TruePositiveLabel = 1
    TruePositive = 2
    FalseNegative = 3


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
        self.evalution = AnnoteEvaluation.noEvaluation
        assert (className != None) or (classNumber != None)
        if classNumber == None:
            self.className = className
            self.classNumber = GetClassNumber(self.className)
        elif className == None:
            self.classNumber = classNumber
            self.className = GetClassName(self.classNumber)
        else:
            self.classNumber = classNumber
            self.className = className

    @property
    def width(self):
        """Returns width."""
        return self.box[2] - self.box[0]

    @property
    def height(self):
        """Returns height."""
        return self.box[3] - self.box[1]

    @property
    def class_abbrev(self):
        """Returns class abbrev."""
        # Split text by '.'
        values = self.className.split(".")

        # Max 3 letters from front
        return values[0][:3].upper()

    def SetClassNumber(self, number):
        """Returns class number."""
        self.classNumber = number
        self.className = GetClassName(number)

    def SetAuthorType(self, authorType):
        """Returns author type."""
        self.authorType = authorType

    def SetEvalution(self, evalution):
        """Returns author type."""
        self.evalution = evalution

    def GetClassNumber(self):
        """Returns class number."""
        return self.classNumber

    def GetClassName(self):
        """Returns class name."""
        return self.className

    def GetBox(self):
        """Returns box."""
        return self.box

    def GetAuthorType(self):
        """Returns author type."""
        return self.authorType

    def GetConfidence(self):
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

    def QtDraw(self, painter, highlight=False, isConfidence=True, isLabel=True):
        """Draw self."""
        width, height = painter.window().getRect()[2:]
        x1, y1, x2, y2 = boxes.ToAbsolute(self.box, width, height)

        # Label text
        label = self.className
        # Thicknes of border
        thickness = 1
        if highlight is True:
            thickness = 2

        # Human orignal from file detection
        if self.authorType == AnnoteAuthorType.byHuman:
            if self.evalution in [
                AnnoteEvaluation.noEvaluation,
                AnnoteEvaluation.TruePositiveLabel,
            ]:
                brushColor = Qt.black
            elif self.evalution == AnnoteEvaluation.TruePositive:
                brushColor = Qt.darkYellow
            elif self.evalution == AnnoteEvaluation.FalseNegative:
                brushColor = Qt.red

        # Created by detector YOLO
        elif self.authorType == AnnoteAuthorType.byDetector:
            brushColor = Qt.darkBlue
            label = "{}".format(self.className)
            # If confidence drawing enabled
            if isConfidence:
                label += "[{:.2f}]".format(float(self.confidence))

        # Created by hand
        elif self.authorType == AnnoteAuthorType.byHand:
            brushColor = Qt.darkGreen

        # Draw rectangle box
        QDrawRectangle(
            painter,
            [QPoint(x1, y1), QPoint(x2, y2)],
            pen=brushColor,
            penThickness=thickness,
            brushColor=brushColor,
            brushOpacity=0.25,
        )

        # Text
        if isLabel:
            QDrawText(
                painter,
                QPoint(x1, y1),
                label,
                bgColor=brushColor,
                textAlign="bottomright",
            )

    def IsInside(self, point):
        """True if point is inside note box."""
        return boxes.IsInside(point, self.box)
