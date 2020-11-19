'''
Created on 17 lis 2020

@author: spasz
'''
import os
import cv2
import logging
import engine.annote as annote
import helpers.prefilters as prefilters
from helpers.files import IsImageFile
from helpers.textAnnotations import ReadAnnotations, SaveAnnotations, IsExistsAnnotations


class Annoter():
    '''
    classdocs
    '''

    def __init__(self, filepath, detector, isOnlyNewFiles=False):
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
        # if only new files - then filter all files with annotation.
        if (isOnlyNewFiles == True):
            self.filenames = [f for f in self.filenames if (
                IsExistsAnnotations(self.dirpath+f) == False)]

        # Current file number offset
        self.offset = 0
        self.image = None
        self.annotations = None
        self.errors = []

    def __getFilename(self):
        ''' Returns current filepath.'''
        return self.filenames[self.offset]

    def GetErrors(self):
        ''' Returns current errors list.'''
        return self.errors

    def GetImage(self):
        ''' Returns current image.'''
        return self.image

    def GetImageNumber(self):
        ''' Returns current image number.'''
        return self.offset

    def GetImagesCount(self):
        ''' Returns count of processed images number.'''
        return len(self.filenames)

    def SetImageNumber(self, number):
        ''' Sets current image number.'''
        if (number >= 0) and (number < len(self.filenames)):
            self.offset = number
            self.Process()
            return True

        return False

    def GetAnnotations(self):
        ''' Returns current annotations.'''
        return self.annotations

    def AddAnnotation(self, box, classNumber):
        ''' Adds new annotation by human.'''
        self.annotations.append(annote.Annote(
            box, classNumber=classNumber, authorType=annote.AnnoteAuthorType.byHand))
        logging.debug('(Annoter) Added annotation class %u!', classNumber)
        self.errors = self.__checkOfErrors()

    def ClearAnnotations(self):
        ''' Clear all annotations.'''
        self.annotations = []
        self.errors = self.__checkOfErrors()
        logging.debug('(Annoter) Cleared annotations!')

    def RemoveAnnotation(self, element):
        '''Remove annotation .'''
        if (len(self.annotations) != 0):
            self.annotations.remove(element)
            self.errors = self.__checkOfErrors()

    def IsSynchronized(self):
        ''' Is image synchronized with file annotations.'''
        isSynchronized = True
        for element in self.annotations:
            if (element.GetAuthorType() != annote.AnnoteAuthorType.byHuman):
                isSynchronized = False
                break

        return isSynchronized

    def Save(self):
        ''' Save current annotations.'''
        self.errors = self.__checkOfErrors()
        if (len(self.errors) == 0):
            annotations = [annote.toTxtAnnote(el) for el in self.annotations]
            annotations = SaveAnnotations(
                self.dirpath+self.__getFilename(), annotations)
            logging.debug('(Annoter) Saved annotations for %s!',
                          self.__getFilename())
            # Process file again after save
            self.Process()
        else:
            logging.error('(Annoter) Errors exists in annotations!')

    def IsEnd(self):
        '''True if files ended.'''
        return (self.offset == len(self.filenames))

    def __checkOfErrors(self):
        '''Check current image/annotations for errors.'''
        errors = []
        if (len(self.annotations) != len(prefilters.FilterIOUbyConfidence(self.annotations))):
            logging.error('(Annoter) Annotations overrides each other!')
            errors.append('Override error!')

        return errors

    def Process(self, forceDetector=False):
        ''' process file.'''
        if (self.offset >= 0) and (self.offset < len(self.filenames)):
            f = self.__getFilename()

            # Read image
            im = cv2.imread(self.dirpath+f)

            annotations = []
            # If exists annotations file
            if (IsExistsAnnotations(self.dirpath+f)):
                txtAnnotes = ReadAnnotations(self.dirpath+f)
                txtAnnotes = [annote.fromTxtAnnote(el) for el in txtAnnotes]
                logging.debug(
                    '(Annoter) Loaded annotations from %s!', self.dirpath+f)
                annotations += txtAnnotes

            # if annotations file not exists or empty then detect.
            if (len(annotations) == 0) or (forceDetector is True):
                detAnnotes = self.detector.Detect(
                    im, confidence=0.1, boxRelative=True)
                detAnnotes = [annote.fromDetection(el) for el in detAnnotes]
                detAnnotes = prefilters.FilterIOUbyConfidence(detAnnotes)
                logging.debug(
                    '(Annoter) Detected annotations for %s!', self.dirpath+f)
                annotations += detAnnotes

            self.image = im
            self.annotations = annotations

            # Post-check of errors
            self.errors = self.__checkOfErrors()

            return True

        return False

    def ProcessNext(self):
        ''' Process next image.'''
        if (self.offset < (len(self.filenames)-1)):
            self.offset += 1
            self.Process()
            return True

        return False

    def ProcessPrev(self):
        ''' Process next image.'''
        if (self.offset > 0):
            self.offset -= 1
            self.Process()
            return True

        return False
