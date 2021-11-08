'''
Created on 25 cze 2021

@author: spasz
'''
import os
import logging
import pandas as pd
import cv2
from helpers.files import FixPath, GetExtension
import matplotlib.pyplot as plt
import matplotlib
from helpers.textAnnotations import ReadAnnotations, SaveAnnotations,\
    IsExistsImage, GetImageFilepath

matplotlib.use('Agg')
logging.getLogger('matplotlib.font_manager').disabled = True


class Distribution:
    '''
    classdocs
    '''

    def __init__(self,
                 dirpath,
                 renameClass=None,
                 checks=False):
        '''
        Constructor
        '''
        # Processing dirpath
        self.dirpath = dirpath
        # Labels and values
        self.labels = {}
        # Extra checks
        self.checks = checks
        # Rename class x to y
        self.rename = None
        if (renameClass is not None):
            parts = renameClass.split(':')
            if (len(parts) == 2):
                self.rename = {int(parts[0]): int(parts[1])}

        self.Process(dirpath)

    def Process(self, dirpath):
        ''' Process files list.'''
        dirpath = FixPath(dirpath)
        # For every file
        for filepath in os.listdir(dirpath):
            # Check if annotation's
            if (GetExtension(filepath) == '.txt'):
                # Open annotations files
                annotations = ReadAnnotations(dirpath+filepath)
                # Correct all annotations
                correctedAnnotations = [self.__CorrectAnnotationRect(
                    entry) for entry in annotations]
                # Rename annotations if enabled
                correctedAnnotations = [self.__RenameAnnotation(
                    entry) for entry in annotations]
                # If annotaions were wrong then correct file
                if (annotations != correctedAnnotations):
                    annotations = correctedAnnotations
                    SaveAnnotations(dirpath+filepath, annotations)
                # Add annotations to distribution
                for entry in annotations:
                    self.__AddEntryToDistribution(entry)

                # Do extra checks
                if (self.checks is True):
                    if (IsExistsImage(dirpath+filepath) is True):
                        path = GetImageFilepath(dirpath+filepath)
                        # Check file size
                        if (os.stat(path).st_size == 0):
                            logging.error('Image %s size equal to zero!', path)

                        # Check if image is readable
                        if (cv2.imread(path) is None):
                            logging.error('Image %s not readable!', path)

                    else:
                        logging.error(
                            'Not existing image for %s.', dirpath+filepath)

        logging.info('(Distribution) Processed distribution. Found:')
        logging.info(self.labels)

    def __CorrectAnnotationRect(self, entry):
        ''' Corrects annotation rectangle if
            is wrong.'''
        label, bbox = entry
        bbox = [*bbox]
        # All values should be inside range (0.0 .. 1.0)
        for i, value in enumerate(bbox):
            bbox[i] = max(0, min(value, 1.0))

        return (label, (*bbox,))

    def __RenameAnnotation(self, entry):
        ''' Rename annotations label.'''
        label, bbox = entry
        # Check and rename
        if (self.rename is not None):
            if (label in self.rename.keys()):
                label = self.rename[label]

        return (label, bbox)

    def __AddEntryToDistribution(self, entry):
        '''Store entry.'''
        label = entry[0]
        if (label in self.labels.keys()):
            self.labels[label] += 1
        else:
            self.labels[label] = 1

    def Save(self, dirpath):
        ''' Save & plot distribution.'''
        dirpath = FixPath(dirpath)
        # Save .csv
        df = pd.DataFrame({'Labels': [key for key in self.labels.keys()],
                           'Counts': [key for key in self.labels.values()]})
        df = df.sort_values(by=['Labels'])
        df.to_csv(dirpath+'distribution.csv',
                  sep=';', decimal=',', index=False)
        logging.info('(Distribution) Created `%s`.',
                     dirpath+'distribution.csv')

        # Save .png
        plt.bar(df['Labels'].values, df['Counts'].values, label='Labels')

        # Description
        plt.xlabel('Labels')
        plt.ylabel('Counts [j]')
        plt.legend()
        plt.grid()
        plt.yticks(ticks=range(0, max(df['Counts'].values), 500))
        plt.xticks(ticks=range(len(df['Labels'])), rotation=45)

        # Save figure
        plt.savefig(dirpath+'distribution.png')
        logging.info('(Distribution) Created `%s`.',
                     dirpath+'distribution.png')
