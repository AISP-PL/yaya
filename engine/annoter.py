'''
Created on 17 lis 2020

@author: spasz
'''
import os
import cv2
import engine.annote as annote
from helpers.files import IsImageFile
from helpers.textAnnotations import ReadAnnotations, IsExistsAnnotations


class Annoter():
    '''
    classdocs
    '''

    def __init__(self, filepath, detector):
        '''
        Constructor
        '''
        self.detector = detector
        self.dirpath = filepath

        # filter only images and not excludes
        excludes = ['.', '..', './', '.directory']
        filenames = os.listdir(self.dirpath)
        self.filenames = [f for f in filenames if (
            f not in excludes) and (IsImageFile(f))]

        # Current file number offset
        self.offset = 0
        self.image = None
        self.annotations = None

    def GetImage(self):
        ''' Returns current image.'''
        return self.image

    def GetAnnotations(self):
        ''' Returns current annotations.'''
        return self.annotations

    def IsEnd(self):
        '''True if files ended.'''
        return (self.offset == len(self.filenames))

    def Process(self, f):
        ''' process file.'''
        # Read image
        im = cv2.imread(self.dirpath+f)

        # If exists annotations file
        if (IsExistsAnnotations(self.dirpath+f)):
            annotations = ReadAnnotations(self.dirpath+f)
            annotations = [annote.fromTxtAnnote(el) for el in annotations]
        # else detect by YOLO
        else:
            annotations = self.detector.Detect(
                im, confidence=0.3, boxRelative=True)
            annotations = [annote.fromDetection(el) for el in annotations]

        return im, annotations

    def ProcessNext(self):
        ''' Process next image.'''
        if (self.offset < len(self.filenames)):
            f = self.filenames[self.offset]
            self.image, self.annotations = self.Process(f)
            self.offset += 1
            return True

        return False

    def ProcessPrev(self):
        ''' Process next image.'''
        if (self.offset > 0):
            f = self.filenames[self.offset]
            self.image, self.annotations = self.Process(f)
            self.offset -= 1
            return True

        return False
