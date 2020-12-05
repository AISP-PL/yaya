'''
Created on 10 wrz 2020

@author: spasz
'''

from pathlib import Path
import logging
import os


def GetFilename(path):
    ''' Returns filename without extension'''
    return os.path.splitext(path)[0]


def GetExtension(path):
    ''' Returns extension'''
    return os.path.splitext(path)[1]


def CreateOutputDirectory(filepath):
    # Create output path
    path = '%s' % (filepath)
    Path(path).mkdir(parents=True, exist_ok=True)


def IsImageFile(filepath):
    ''' Checks if file is image file.'''
    return GetExtension(filepath).lower() in ['.gif', '.png', '.jpg', '.jpeg', '.tiff']


def DeleteFile(path):
    '''Delete annotations file.'''
    if os.path.exists(path):
        os.remove(path)
        logging.info('Deleted %s.', path)
