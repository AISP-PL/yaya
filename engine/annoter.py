'''
Created on 17 lis 2020

@author: spasz
'''
import os
import cv2
import logging
import engine.annote as annote
import helpers.prefilters as prefilters
import helpers.transformations as transformations
import helpers.boxes as boxes
from helpers.files import IsImageFile, DeleteFile, GetNotExistingSha1Filepath, FixPath, GetFilename,\
    GetExtension
from helpers.textAnnotations import ReadAnnotations, SaveAnnotations, IsExistsAnnotations,\
    DeleteAnnotations


class Annoter():
    '''
    classdocs
    '''
    # Sort methods
    NoSort = 0
    SortByDatetime = 1
    SortByInvDatetime = 2
    SortByAlphabet = 3

    def __init__(self,
                 filepath,
                 detector,
                 noDetector=False,
                 sortMethod=NoSort,
                 isOnlyNewFiles=False,
                 isOnlyOldFiles=False,
                 isOnlyErrorFiles=False,
                 isOnlyDetectedClass=None,
                 isOnlySpecificClass=None):
        '''
        Constructor
        '''
        # Set configuration
        self.config = {
             'sortMethod':sortMethod,
             'isOnlyNewFiles':isOnlyNewFiles,
             'isOnlyOldFiles':isOnlyOldFiles,
             'isOnlyErrorFiles':isOnlyErrorFiles,
             'isOnlyDetectedClass':isOnlyDetectedClass,
             'isOnlySpecificClass':isOnlySpecificClass,
        }
        # Detector handle
        self.detector = detector
        # Path
        self.dirpath = filepath
        # Use of detector
        self.noDetector = noDetector

        # Current file number offset
        self.annotations = None
        self.image = None
        self.offset = 0
        # Set of all errors
        self.errors = set()
        
        self.OpenLocation(self.dirpath)

    def __del__(self):
        ''' Destructor.'''
        # filter only images and not excludes
        excludes = ['.', '..', './', '.directory']
        filenames = os.listdir(self.dirpath)

        # Filter images only
        filenames = [f for f in filenames if (
            f not in excludes) and (IsImageFile(f))]

        # Get only images with annotations
        filenamesAnnotated = [f for f in filenames if (
            IsExistsAnnotations(self.dirpath+f) == True)]

        # Save results
        datasetPath = FixPath(self.dirpath)+'dataset.txt'
        with open(datasetPath, 'w') as f:
            for line in filenamesAnnotated:
                f.write(line+'\n')

            logging.info('(Annoter) Created list of %u/%u annotated images in `%s`.',
                         len(filenamesAnnotated),
                         len(filenames),
                         datasetPath)
    
    def OpenLocation(self, path):
        ''' Open images/annotations location.'''
        # Update dirpath
        self.dirpath = path
        # filter only images and not excludes
        excludes = ['.', '..', './', '.directory']
        filenames = os.listdir(path)

        # Sorting : by datetime
        if (self.config['sortMethod'] == self.SortByDatetime):
            filenames = sorted(filenames,
                               key=lambda f: -os.lstat(path+f).st_mtime)
        elif (self.config['sortMethod'] == self.SortByInvDatetime):
            filenames = sorted(filenames,
                               key=lambda f: os.lstat(path+f).st_mtime)
        # Sorting : by alphabet
        elif (self.config['sortMethod'] == self.SortByDatetime):
            filenames = sorted(filenames)

        # Filter images only
        self.filenames = [f for f in filenames if (
            f not in excludes) and (IsImageFile(f))]

        # if only new files - then filter all files with annotation.
        if (self.config['isOnlyNewFiles'] == True):
            self.filenames = [f for f in self.filenames if (
                IsExistsAnnotations(path+f) == False)]

        # if only new files - then filter all files without annotation.
        elif (self.config['isOnlyOldFiles'] == True):
            self.filenames = [f for f in self.filenames if (
                IsExistsAnnotations(path+f) == True)]

        # Use only files with errors
        if (self.config['isOnlyErrorFiles'] == True):
            filesWithErrors = []
            for offset, filename in enumerate(self.filenames):
                self.offset = offset
                self.Process()
                if (len(self.errors) != 0):
                    filesWithErrors.append(filename)

            self.filenames = filesWithErrors

        # Use only files with specific class detected
        if (self.config['isOnlyDetectedClass'] is not None):
            filesForClass = []
            for offset, filename in enumerate(self.filenames):
                self.offset = offset
                self.Process(processImage=True, forceDetector=True)
                # Check if detected class exists in annotations
                if (len(self.annotations) != 0) and  \
                        (len(self.GetAnnotationsForClass(self.config['isOnlyDetectedClass'])) != 0):
                    filesForClass.append(filename)
                # Logging progress
                logging.info('Progress : [%u/%u]\r',
                             offset, len(self.filenames))

            self.filenames = filesForClass

        # Use only files with specific class
        if (self.config['isOnlySpecificClass'] is not None):
            filesForClass = []
            for offset, filename in enumerate(self.filenames):
                self.offset = offset
                self.Process(processImage=False)
                if (len(self.annotations) != 0) and  \
                        (len(self.GetAnnotationsForClass(self.config['isOnlySpecificClass'])) != 0):
                    filesForClass.append(filename)

            self.filenames = filesForClass

        # Reset values at the end
        self.annotations = None
        self.image = None
        self.offset = 0
        self.errors = set()

    def GetFilename(self):
        ''' Returns current filepath.'''
        return self.filenames[self.offset]

    def GetFilepath(self):
        ''' Returns current filepath.'''
        return self.dirpath+self.filenames[self.offset]

    def GetErrors(self):
        ''' Returns current errors list.'''
        return self.errors

    def GetImage(self):
        ''' Returns current image.'''
        return self.image

    def GetImageSize(self):
        ''' Returns current image.'''
        if (self.image is not None):
            h, w, bytes = self.image.shape
            return w, h, bytes

        return 0, 0, 0

    def GetImageNumber(self):
        ''' Returns current image number.'''
        return self.offset

    def GetImagesList(self):
        ''' Returns images list'''
        return self.filenames

    def GetAnnotationsList(self):
        ''' Returns annotations list'''
        return [GetFilename(f)+'.txt' for f in self.filenames]

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

    def TransformShape(self, mode='Flip'):
        ''' Transform image and annotations shape.'''
        if (mode == 'Flip'):
            self.image = transformations.Flip(self.image)
            for a in self.annotations:
                a.box = boxes.FlipHorizontally(1, a.box)

        # Store image modification info
        for a in self.annotations:
            a.authorType = annote.AnnoteAuthorType.byHuman
        self.errors.add('ImageModified!')

    def PaintCircles(self, points, radius, color):
        ''' Paint list of circles Circle on image.'''
        for x, y in points:
            self.image = cv2.circle(self.image,
                                    (round(x), round(y)),
                                    radius,
                                    color,
                                    -1)
        self.errors.add('ImageModified!')

    def GetAnnotations(self):
        ''' Returns current annotations.'''
        return self.annotations

    def GetAnnotationsForClass(self, classNumber):
        ''' Returns current annotations.'''
        annotations = [a for a in self.annotations if (
            a.classNumber == classNumber)]
        return annotations

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
        ''' Is all annotations synchronized with file.'''
        isSynchronized = True
        for element in self.annotations:
            if (element.GetAuthorType() != annote.AnnoteAuthorType.byHuman):
                isSynchronized = False
                break

        return isSynchronized

    def __isClearImageSynchronized(self):
        ''' True if image was modified.'''
        result = not ('ImageModified!' in self.errors)
        if (result is False):
            self.errors.remove('ImageModified!')
        return result

    def Delete(self):
        ''' Deletes current image and annotations.'''
        f = self.GetFilename()
        if (f in self.filenames):
            DeleteAnnotations(self.dirpath+f)
            self.ClearAnnotations()
            DeleteFile(self.dirpath+f)
            self.filenames.remove(f)
            # TODO correct offset

    def Create(self):
        ''' Creates new filepath for new image file.'''
        filename = self.GetFilename()
        filename, filepath = GetNotExistingSha1Filepath(
            filename, self.dirpath)
        cv2.imwrite('%s' % (filepath), self.image)
        self.filenames.insert(self.offset, filename)
        logging.info('(Annoter) New image %s created!', filename)

    def Save(self):
        ''' Save current annotations.'''
        filename = self.GetFilename()

        # If image was modified, then save it also
        if (self.__isClearImageSynchronized() == False):
            # Create temporary and original paths
            imgpath = FixPath(self.dirpath) + filename
            tmppath = FixPath(self.dirpath) + 'tmp' + GetExtension(filename)
            # Save temporary image
            result = cv2.imwrite(tmppath, self.image)
            # If saved then atomic move image to original image
            if (result is True):
                os.system('mv -fv %s %s ' % (tmppath, imgpath))
            else:
                logging.error('(Annoter) Writing image %s failed!', imgpath)

        # Check other errors
        self.errors = self.__checkOfErrors()
        if (len(self.errors) == 0):
            # Save annotations
            annotations = [annote.toTxtAnnote(el) for el in self.annotations]
            annotations = SaveAnnotations(
                self.dirpath+filename, annotations)
            logging.debug('(Annoter) Saved annotations for %s!', filename)

            # Process file again after save
            self.Process()
        else:
            logging.error('(Annoter) Errors exists in annotations!')

    def IsEnd(self):
        '''True if files ended.'''
        return (self.offset == len(self.filenames))

    def __checkOfErrors(self):
        '''Check current image/annotations for errors.'''
        errors = set()
        if (len(self.annotations) != len(prefilters.FilterIOUbyConfidence(self.annotations, self.annotations))):
            logging.error('(Annoter) Annotations overrides each other!')
            errors.add('Override error!')

        return errors

    def Process(self,
                processImage=True,
                forceDetector=False):
        ''' process file.'''
        if (self.offset >= 0) and (self.offset < len(self.filenames)):
            f = self.GetFilename()

            # Read image
            if (processImage is True):
                im = cv2.imread(self.dirpath+f)
                self.image = im

            annotations = []
            txtAnnotes = []
            detAnnotes = []
            # If exists annotations file
            if (IsExistsAnnotations(self.dirpath+f)):
                txtAnnotes = ReadAnnotations(self.dirpath+f)
                txtAnnotes = [annote.fromTxtAnnote(el) for el in txtAnnotes]
                logging.debug(
                    '(Annoter) Loaded annotations from %s!', self.dirpath+f)
                annotations += txtAnnotes

            # if annotations file not exists or empty then detect.
            if (self.noDetector is False) and (processImage is True) and ((len(annotations) == 0) or (forceDetector is True)):
                # Call detector
                detAnnotes = self.detector.Detect(
                    im, confidence=0.3, boxRelative=True)
                logging.debug(
                    '(Annoter) %u annotations to process.', len(detAnnotes))
                # Create annotes
                detAnnotes = [annote.fromDetection(el) for el in detAnnotes]
                # Filter by IOU internal with same annotes
                # and also with txt annotes.
                detAnnotes = prefilters.FilterIOUbyConfidence(detAnnotes,
                                                              detAnnotes + txtAnnotes)
                logging.debug(
                    '(Annoter) Detected %u annotations for %s!',
                    len(detAnnotes),
                    self.dirpath+f)
                annotations += detAnnotes

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
