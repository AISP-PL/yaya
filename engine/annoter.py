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
from helpers.metrics import mAP, dSurplus


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
                 sortMethod=SortByInvDatetime,
                 isOnlyNewFiles=False,
                 isOnlyOldFiles=False,
                 isOnlyErrorFiles=False,
                 isOnlyDetectedClass=None,
                 isOnlySpecificClass=None,
                 forceDetector=False,
                 ):
        '''
        Constructor
        '''
        # Set configuration
        self.config = {
            'sortMethod': sortMethod,
            'forceDetector': forceDetector,
            'isOnlyNewFiles': isOnlyNewFiles,
            'isOnlyOldFiles': isOnlyOldFiles,
            'isOnlyErrorFiles': isOnlyErrorFiles,
            'isOnlyDetectedClass': isOnlyDetectedClass,
            'isOnlySpecificClass': isOnlySpecificClass,
        }
        # Detector handle
        self.detector = detector
        # Path
        self.dirpath = filepath
        # Use of detector
        self.noDetector = noDetector

        # File entries list
        self.files = None
        # Annotations list
        self.annotations = []
        # Readed image cv2 object
        self.image = None
        # Current file number offset
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

    def GetFileAnnotations(self, filepath):
        ''' Read file annotations if possible.'''
        txtAnnotes = []
        # If exists annotations file
        if (IsExistsAnnotations(filepath)):
            txtAnnotes = ReadAnnotations(filepath)
            txtAnnotes = [annote.fromTxtAnnote(el) for el in txtAnnotes]
            logging.debug(
                '(Annoter) Loaded annotations from %s!', filepath)

            # Post-check of errors
            self.errors = self.__checkOfErrors()

        return txtAnnotes

    def GetFileImage(self, filepath):
        ''' Read file annotations if possible.'''
        im = None
        if (os.path.exists(filepath)):
            im = cv2.imread(filepath)

        return im

    def GetFileDetections(self, im, filepath, txtAnnotes):
        ''' Read file annotations if possible.'''
        if (self.detector is None) or (im is None):
            return [], 0, 0

        # Call detector
        detAnnotes = self.detector.Detect(
            im, confidence=0.3, boxRelative=True)
        logging.debug(
            '(Annoter) %u annotations to process.', len(detAnnotes))
        # Create annotes
        detAnnotes = [annote.fromDetection(el) for el in detAnnotes]
        # Calculate mAP
        detections_mAP = mAP(txtAnnotes, detAnnotes)
        detections_dSurplus = dSurplus(txtAnnotes, detAnnotes)

        # Filter by IOU internal with same annotes
        # and also with txt annotes.
        detAnnotes = prefilters.FilterIOUbyConfidence(detAnnotes,
                                                      detAnnotes + txtAnnotes)
        logging.debug(
            '(Annoter) Detected %u annotations with %2.2fmAP for %s!',
            len(detAnnotes),
            detections_mAP,
            filepath)

        return detAnnotes, detections_mAP, detections_dSurplus

    def OpenLocation(self, path):
        ''' Open images/annotations location.'''
        # Update dirpath
        self.dirpath = path
        # filter only images and not excludes
        excludes = ['.', '..', './', '.directory']

        # ---------- Filtering -----------
        self.files = []
        for index, filename in enumerate(os.listdir(path)):
            # Filter excludes
            if (filename in excludes):
                continue

            # Filter not images
            if (not IsImageFile(filename)):
                continue

            # Check if annotations exists
            isAnnotation = IsExistsAnnotations(path+filename)

            # Read annotations
            txtAnnotations = self.GetFileAnnotations(path+filename)

            # Force detector if needed
            detections, detections_mAP, detections_dSurplus = None, None, None
            if (self.config['forceDetector'] == True):
                im = self.GetFileImage(path+filename)
                detections, detections_mAP, detections_dSurplus = self.GetFileDetections(
                    im, path+filename, txtAnnotations)

            # Add file entry
            self.files.append({
                'Name': filename,
                'Path': path+filename,
                'ID': index,
                'IsAnnotation': isAnnotation,
                'Annotations': txtAnnotations,
                'Datetime': os.lstat(path+filename).st_mtime,
                'Errors': len(self.errors),
                'Detections': detections,
                'mAP': detections_mAP,
                'dSurplus': detections_dSurplus,
            })

            # Logging progress
            logging.info('Progress : [%u]\r',
                         index)

        # ------- Sorting ------------
        # Sorting : by datetime
        if (self.config['sortMethod'] == self.SortByDatetime):
            self.files = sorted(self.files,
                                key=lambda i: i['Datetime'])
        elif (self.config['sortMethod'] == self.SortByInvDatetime):
            self.files = sorted(self.files,
                                key=lambda i: -i['Datetime'])
        # Sorting : by alphabet
        elif (self.config['sortMethod'] == self.SortByAlphabet):
            self.files = sorted(self.files,
                                key=lambda i: i['Name'])

        # ------- Extra processing ------------
        # Use only files with errors
        if (self.config['isOnlyErrorFiles'] == True):
            filesWithErrors = []
            for index, fileEntry in enumerate(self.files):
                if (fileEntry['Errors'] != 0):
                    filesWithErrors.append(fileEntry)

            # Swap with files
            self.files = filesWithErrors

        # Use only files with specific class
        if (self.config['isOnlySpecificClass'] is not None):
            filesForClass = []
            for offset, fileEntry in enumerate(self.files):
                annotations = self.AnnotationsSelectClasses(
                    fileEntry['Annotations'], [self.config['isOnlySpecificClass']])
                if (annotations is not None) and (len(annotations) != 0):
                    filesForClass.append(fileEntry)

            self.files = filesForClass

        # Reset values at the end
        self.annotations = []
        self.image = None
        self.offset = 0
        self.errors = set()

    def GetFile(self):
        ''' Returns current filepath.'''
        if (len(self.files)):
            return self.files[self.offset]

        return None

    def GetFilename(self):
        ''' Returns current filepath.'''
        if (len(self.files)):
            return self.files[self.offset]['Name']

        return 'Not exists!'

    def GetFilepath(self):
        ''' Returns current filepath.'''
        return self.files[self.offset]['Path']

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

    def GetAnnotationsList(self):
        ''' Returns annotations list'''
        return [GetFilename(f['Name'])+'.txt' for f in self.files]

    def GetFiles(self):
        ''' Returns images list'''
        return self.files

    def GetFileID(self):
        ''' Returns current image ID.'''
        return self.files[self.offset]['ID']

    def GetFileIndex(self):
        ''' Returns current image number.'''
        return self.offset

    def GetFilesCount(self):
        ''' Returns count of processed images number.'''
        return len(self.files)

    def GetFilesAnnotatedCount(self):
        ''' Returns count of processed images number.'''
        annotated = sum([int(fileEntry['IsAnnotation'])
                         for fileEntry in self.files])
        return annotated

    def SetImageID(self, fileID):
        ''' Sets current image number.'''
        # index of ID file
        foundIndex = None
        # Find image with these id
        for index, fileEntry in enumerate(self.files):
            if (fileEntry['ID'] == fileID):
                foundIndex = index
                break

        if (foundIndex is not None) and (foundIndex) and (foundIndex < len(self.files)):
            self.offset = foundIndex
            self.Process()
            return True

        return False

    def SetImageNumber(self, number):
        ''' Sets current image number.'''
        if (number >= 0) and (number < len(self.files)):
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

    @staticmethod
    def AnnotationsSelectClasses(annotations, classes):
        ''' Returns current annotations.'''
        if (annotations is not None):
            annotations = [a for a in annotations if (
                a.classNumber in classes)]

        return annotations

    def GetAnnotationsSelectClasses(self, classes):
        ''' Returns current annotations.'''
        return self.AnnotationsSelectClasses(self.annotations, classes)

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

    def Delete(self, fileEntry=None):
        ''' Deletes image and annotations.'''
        # If not specified fileEntry then use
        # current fileEntry.
        if (fileEntry is None):
            # Use current file
            if (self.offset < self.GetFilesCount()):
                fileEntry = self.files[self.offset]

        # If entry exists then delete it
        if (fileEntry is not None):
            self.ClearAnnotations()
            DeleteAnnotations(fileEntry['Path'])
            DeleteFile(fileEntry['Path'])
            self.files.remove(fileEntry)

            # Step back offset
            self.offset = min(self.offset,
                              self.GetFilesCount()-1)

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
                os.system('mv -fv "%s" "%s" ' % (tmppath, imgpath))
            else:
                logging.error('(Annoter) Writing image "%s" failed!', imgpath)

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

        # Update file entry
        self.files[self.offset]['IsAnnotation'] = (len(self.annotations) != 0)
        self.files[self.offset]['Annotations'] = self.annotations

    def IsEnd(self):
        '''True if files ended.'''
        return (self.offset == self.GetFilesCount())

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
        if (self.offset >= 0) and (self.offset < self.GetFilesCount()):
            fileEntry = self.GetFile()

            # Read image
            if (processImage is True):
                self.image = im = self.GetFileImage(fileEntry['Path'])

            # All txt annotations
            txtAnnotes = self.GetFileAnnotations(fileEntry['Path'])
            # Detector annotations list
            detAnnotes = []
            # if annotations file not exists or empty then detect.
            if (self.noDetector is False) and (processImage is True) and ((len(txtAnnotes) == 0) or (forceDetector is True)):
                detAnnotes, detections_mAP, detections_dSurplus = self.GetFileDetections(
                    im, fileEntry['Path'], txtAnnotes)
                fileEntry['mAP'] = detections_mAP
                fileEntry['dSurplus'] = detections_dSurplus

            # All annotations
            self.annotations = txtAnnotes + detAnnotes

            # Post-check of errors
            self.errors = self.__checkOfErrors()

            return True

        return False

    def ProcessNext(self):
        ''' Process next image.'''
        if (self.offset < (self.GetFilesCount()-1)):
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
