'''
Created on 10 wrz 2020

@author: spasz
'''

from pathlib import Path
import logging
import os
import fnmatch
from helpers.hashing import GetRandomSha1


def CreateDirectory(path):
    ''' Creates directory.'''
    return Path(path).mkdir(parents=True, exist_ok=True)


def GetFileLocation(path):
    ''' Returns file location '''
    return os.path.dirname(path)


def GetFiles(base, pattern):
    '''Return list of files matching pattern in base folder.'''
    return [n for n in fnmatch.filter(os.listdir(base), pattern) if
            os.path.isfile(os.path.join(base, n))]


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
    if os.path.exists(path) or os.path.islink(path) or os.path.isdir(path):
        os.remove(path)
        logging.info('Deleted %s.', path)


def GetNotExistingSha1Filepath(filename, dirpath):
    ''' Returns new SHA-1 Filepath.'''
    extension = GetExtension(filename).lower()
    newFilepath = dirpath+filename

    # Try random hash until find not existsing file
    while (os.path.isfile(newFilepath) and os.access(newFilepath, os.R_OK)):
        newFilename = GetRandomSha1()+extension
        newFilepath = dirpath+newFilename

    return newFilename, newFilepath


def RenameToSha1Filepath(filename, dirpath):
    ''' Returns new SHA-1 Filepath.'''
    oldFilepath = dirpath+filename
    newFilename, newFilepath = GetNotExistingSha1Filepath(filename, dirpath)
    os.rename(oldFilepath, newFilepath)
    logging.debug('%s -> %s.' % (oldFilepath, newFilepath))
    return newFilename


def FixPath(path):
    '''
        Fix path / character at the end.
        Only works with directory paths.
    '''
    if (path[-1] == '/'):
        return path
    return path+'/'
