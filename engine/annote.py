'''
Created on 17 lis 2020

@author: spasz
'''

import helpers.boxes as boxes
import cv2
from enum import Enum

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
        return 'Invalid'


def GetClassNumber(name):
    ''' Retruns class number '''
    return classNames.index(name)


class AnnoteAuthorType(Enum):
    byHuman = 0
    byDetector = 1


def toTxtAnnote(annote):
    ''' Creates txt annote from object Annote.'''
    classNumber = annote.GetClassNumber()
    box = annote.GetBox()
    return (classNumber, box)


def fromTxtAnnote(txtAnnote):
    ''' Creates Annote from txt annote.'''
    classNumber, box = txtAnnote
    return Annote(box, classNumber=classNumber, authorType=AnnoteAuthorType.byHuman)


def fromDetection(detection):
    ''' Creates Annote from txt annote.'''
    className, confidence, box = detection
    return Annote(box, className=className, confidence=confidence, authorType=AnnoteAuthorType.byDetector)


class Annote():
    '''
    classdocs
    '''

    def __init__(self, box, classNumber=None, className=None, confidence=1.00, authorType=AnnoteAuthorType.byHuman):
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

    def GetClassNumber(self):
        ''' Returns class number.'''
        return self.classNumber

    def GetBox(self):
        ''' Returns box.'''
        return self.box

    def Draw(self, image):
        ''' Draw self.'''
        h, w = image.shape[0:2]
        x1, y1, x2, y2 = boxes.ToAbsolute(self.box, w, h)
        # Detection rectangle
        if (self.authorType == AnnoteAuthorType.byHuman):
            cv2.rectangle(image, (x1, y1), (x2, y2), (0, 0, 255), 1)
        else:
            cv2.rectangle(image, (x1, y1), (x2, y2), (255, 0, 0), 1)
            image = cv2.line(image, (x1, y1), (x2, y2), (255, 0, 0), 1)
            image = cv2.line(image, (x1, y2), (x2, y1), (255, 0, 0), 1)
        # Text
        cv2.putText(image, '{} [{:.2f}]'.format(self.className, float(self.confidence)),
                    (x1-1, y1 - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                    (0, 0, 0), 3)
        cv2.putText(image, '{} [{:.2f}]'.format(self.className, float(self.confidence)),
                    (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                    (255, 255, 255), 1)

    def IsInside(self, point):
        ''' True if point is inside note box.'''
        return boxes.IsInside(point, self.box)
