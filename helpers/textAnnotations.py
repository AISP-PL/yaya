'''
Created on 16 lis 2020

@author: spasz
'''
import os
from helpers.files import GetFilename, DeleteFile
import helpers.boxes as boxes


def GetImageFilepath(annotationPath):
    ''' Returns image filepath.'''
    path = GetFilename(annotationPath)
    for suffix in ['.png', '.jpeg', '.jpg', '.PNG', '.JPEG', '.JPG']:
        if (os.path.isfile(path+suffix) and os.access(path+suffix, os.R_OK)):
            return path+suffix

    return None


def IsExistsAnnotations(imagePath, extension='.txt'):
    ''' True if exists annotations file.'''
    path = GetFilename(imagePath)+extension
    return os.path.isfile(path) and os.access(path, os.R_OK)


def IsExistsImage(annotationPath):
    ''' True if exists annotations file.'''
    path = GetFilename(annotationPath)
    for suffix in ['.png', '.jpeg', '.jpg', '.PNG', '.JPEG', '.JPG']:
        if (os.path.isfile(path+suffix) and os.access(path+suffix, os.R_OK)):
            return True

    return False


def DeleteAnnotations(imagePath, extension='.txt'):
    '''Delete annotations file.'''
    path = GetFilename(imagePath)+extension
    DeleteFile(path)


def ReadAnnotations(imagePath, extension='.txt'):
    '''Read annotations from file.'''
    annotations = []
    path = GetFilename(imagePath)+extension
    with open(path, 'r') as f:
        for line in f:
            txtAnnote = (line.rstrip('\n').split(' '))
            classNumber = int(txtAnnote[0])
            box = (float(txtAnnote[1]), float(txtAnnote[2]),
                   float(txtAnnote[3]), float(txtAnnote[4]))
            box = boxes.Bbox2Rect(box)
            annotations.append((classNumber, box))

    return annotations


def ReadDetections(imagePath, extension='.txt'):
    '''Read annotations detections from file.'''
    annotations = []
    path = GetFilename(imagePath)+extension
    with open(path, 'r') as f:
        for line in f:
            txtAnnote = (line.rstrip('\n').split(' '))
            className = str(txtAnnote[0])
            confidence = float(txtAnnote[1])
            box = (float(txtAnnote[2]), float(txtAnnote[3]),
                   float(txtAnnote[4]), float(txtAnnote[5]))
            box = boxes.Bbox2Rect(box)
            annotations.append((className, confidence, box))

    return annotations


def SaveAnnotations(imagePath, annotations, extension='.txt'):
    '''Save annotations for file.'''
    path = GetFilename(imagePath)+extension
    with open(path, 'w') as f:
        for element in annotations:
            classNumber, box = element
            box = boxes.Rect2Bbox(box)
            f.write('%u %2.6f %2.6f %2.6f %2.6f\n' %
                    (classNumber, box[0], box[1], box[2], box[3]))


def SaveDetections(imagePath, annotations, extension='.txt'):
    '''Save annotations for file.'''
    path = GetFilename(imagePath)+extension
    with open(path, 'w') as f:
        for element in annotations:
            className, confidence, box = element
            box = boxes.Rect2Bbox(box)
            f.write('%s %2.2f %2.6f %2.6f %2.6f %2.6f\n' %
                    (className, confidence, box[0], box[1], box[2], box[3]))
