'''
Created on 23 lis 2020

@author: spasz
'''

from enum import Enum
import logging
from Gui.drawing import DrawDetections

class NmsMethod(str, Enum):
    ''' Different NMS methods.'''
    Nms = 'Nms'
    SoftNms = 'SoftNms'


class Detector:
    '''
        Detector base class.
    '''

    def __init__(self,
                 gpuid=0,
                 id=255,
                 name=''):
        '''
        Constructor
        '''
        # Detector id
        self.id = id
        # GPU id for multiple gpus
        self.gpuid = gpuid
        # Detector name
        self.name = name
        # List of detector classes/labels
        self.classes = []
        # Colors of labels
        self.colors = []

        logging.debug('(Detector) Created %u.%s!', self.id, self.name)

    def Init(self):
        ''' Init call with other arguments.'''
        # Default implementation

    def Close(self):
        ''' Called after processing whole video.'''
        # Not implemented

    def GetDetector(self):
        ''' Return myself - virtual.'''
        return self

    def Detect(self, image, confidence=0.5, nms_thresh=0.45):
        ''' Detect objects in given image'''
        return []

    def GetName(self):
        ''' Returns detector name.'''
        return self.name

    def GetID(self):
        ''' Returns detector class id.'''
        return self.id

    def GetWidth(self):
        ''' Returns network image width.'''
        return 0

    def GetHeight(self):
        ''' Returns network image height.'''
        return 0

    def Draw(self, image, detections):
        ''' Draw all boxes on image'''
        return DrawDetections(image, detections, self.colors)

    def IsClassesAllowed(self, classes):
        ''' True if classes names are allowed
             within detector.'''
        return set(classes).issubset(self.classes)

    def GetClassNames(self):
        ''' Returns all interesing us class names.'''
        return self.classes

    def GetClassNumber(self, label):
        ''' Return number of label.'''
        if (self.classes is None):
            return -1

        if (label not in self.classes):
            return -1

        return self.classes.index(label)
