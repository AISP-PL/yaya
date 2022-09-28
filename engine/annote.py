'''
Created on 17 lis 2020

@author: spasz
'''

import helpers.boxes as boxes
import cv2
from enum import Enum
from helpers.QtDrawing import QDrawRectangle, QDrawText
from PyQt5.QtCore import QPoint
from PyQt5.QtCore import Qt
import logging

classNames = []


def Init(names):
    ''' Initalize class names list'''
    global classNames
    classNames = names


def GetClasses():
    ''' Returns class name'''
    return classNames


def GetClassName(number):
    ''' Returns class name'''
    if (number < len(classNames)):
        return classNames[number]
    else:
        return 'Invalid_C'+str(number)


def GetClassNumber(name):
    ''' Retruns class number '''
    if (name in classNames):
        return classNames.index(name)

    logging.error('(Annote) Invalid class name %s.', name)
    return 0


class AnnoteAuthorType(Enum):
    byHuman = 0
    byDetector = 1
    byHand = 2


def toTxtAnnote(annote):
    ''' Creates txt annote from object Annote.'''
    classNumber = annote.GetClassNumber()
    box = annote.GetBox()
    return (classNumber, box)


def toYoloDetection(annote):
    ''' Creates YOLOv4 detection from object Annote.'''
    className = annote.GetClassName()
    box = annote.GetBox()
    return (className, 100, box)


def fromTxtAnnote(txtAnnote, defaultAuthor=AnnoteAuthorType.byHuman):
    ''' Creates Annote from txt annote.'''
    classNumber, box = txtAnnote
    return Annote(box, classNumber=classNumber, authorType=defaultAuthor)


def fromDetection(detection):
    ''' Creates Annote from txt annote.'''
    className, confidence, box = detection
    return Annote(box, className=className, confidence=confidence, authorType=AnnoteAuthorType.byDetector)


class Annote():
    '''
    classdocs
    '''

    def __init__(self, box, classNumber=None, className=None, confidence=100.0, authorType=AnnoteAuthorType.byHuman):
        '''
        Constructor
        '''
        self.box = box
        self.confidence = confidence
        self.authorType = authorType
        assert((className != None) or (classNumber != None))
        if (classNumber == None):
            self.className = className
            self.classNumber = GetClassNumber(self.className)
        elif (className == None):
            self.classNumber = classNumber
            self.className = GetClassName(self.classNumber)
        else:
            self.classNumber = classNumber
            self.className = className

    def SetClassNumber(self, number):
        ''' Returns class number.'''
        self.classNumber = number
        self.className = GetClassName(number)

    def SetAuthorType(self, authorType):
        ''' Returns author type.'''
        self.authorType = authorType

    def GetClassNumber(self):
        ''' Returns class number.'''
        return self.classNumber

    def GetClassName(self):
        ''' Returns class name.'''
        return self.className

    def GetBox(self):
        ''' Returns box.'''
        return self.box

    def GetAuthorType(self):
        ''' Returns author type.'''
        return self.authorType

    def GetConfidence(self):
        ''' Returns confidence.'''
        return self.confidence

    def Draw(self, image, highlight=False, isConfidence=True):
        ''' Draw self.'''
        h, w = image.shape[0:2]
        x1, y1, x2, y2 = boxes.ToAbsolute(self.box, w, h)

        # Highlighted annotations have thicker border
        thickness = 1
        if (highlight is True):
            thickness = 2

        # Label text
        label = self.className
        # Human orignal from file detection
        if (self.authorType == AnnoteAuthorType.byHuman):
            cv2.rectangle(image, (x1, y1), (x2, y2), (0, 0, 255), thickness)
        # Created by detector YOLO
        elif (self.authorType == AnnoteAuthorType.byDetector):
            cv2.rectangle(image, (x1, y1), (x2, y2), (255, 0, 0), thickness)
            image = cv2.line(image, (x1, y1), (x2, y2), (255, 0, 0), thickness)
            image = cv2.line(image, (x1, y2), (x2, y1), (255, 0, 0), thickness)
            label = '{}'.format(self.className)
            # If confidence drawing enabled
            if (isConfidence):
                label += '[{:.2f}]'.format(float(self.confidence))

        # Created by hand
        elif (self.authorType == AnnoteAuthorType.byHand):
            cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), thickness)

        # Text
        cv2.putText(image, label,
                    (x1-1, y2 - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                    (0, 0, 0), 3)
        cv2.putText(image, label,
                    (x1, y2 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                    (255, 255, 255), 1)

    def QtDraw(self, painter, highlight=False, isConfidence=True):
        ''' Draw self.'''
        width, height = painter.window().getRect()[2:]
        x1, y1, x2, y2 = boxes.ToAbsolute(self.box, width, height)

        # Label text
        label = self.className
        # Thicknes of border
        thickness = 1
        if (highlight is True):
            thickness = 2

        # Human orignal from file detection
        if (self.authorType == AnnoteAuthorType.byHuman):
            brushColor = Qt.darkRed
        # Created by detector YOLO
        elif (self.authorType == AnnoteAuthorType.byDetector):
            brushColor = Qt.darkBlue
            label = '{}'.format(self.className)
            # If confidence drawing enabled
            if (isConfidence):
                label += '[{:.2f}]'.format(float(self.confidence))

        # Created by hand
        elif (self.authorType == AnnoteAuthorType.byHand):
            brushColor = Qt.darkGreen

        # Draw rectangle box
        QDrawRectangle(painter,
                       [QPoint(x1, y1), QPoint(x2, y2)],
                       pen=brushColor,
                       penThickness=thickness,
                       brushColor=brushColor,
                       brushOpacity=0.1
                       )

        # Text
        QDrawText(painter,
                  QPoint(x1, y1),
                  label,
                  bgColor=brushColor,
                  textAlign='bottomright'
                  )

    def IsInside(self, point):
        ''' True if point is inside note box.'''
        return boxes.IsInside(point, self.box)
