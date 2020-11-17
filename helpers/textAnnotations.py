'''
Created on 16 lis 2020

@author: spasz
'''
import os
from helpers.files import * 

def __getAnnotationFilepath(imagePath):
    ''' Returns annotation filepath.'''
    return GetFilename(imagePath) + '.txt'

def IsExistsAnnotations(imagePath):
    ''' True if exists annotations file.'''
    path = __getAnnotationFilepath(imagePath)
    return os.path.isfile(path) and os.access(path, os.R_OK)

def ReadAnnotations(imagePath):
    '''Read annotations from file.'''
    annotations=[]
    path = __getAnnotationFilepath(imagePath)
    with open(path, 'r') as f:
        for line in f:
            annotations.append(line.rstrip('\n').split(' '))
    
    return annotations