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
from PIL import Image
from helpers.textAnnotations import ReadAnnotations, SaveAnnotations,\
    IsExistsImage, GetImageFilepath
from Decorators.DecoratorDistributionShowcase import DecoratorDistributionShowcase
from helpers.boxes import GetWidth, GetHeight

matplotlib.use('Agg')
logging.getLogger('matplotlib.font_manager').disabled = True
logging.getLogger('PIL.PngImagePlugin').disabled = True
logging.getLogger('PIL.TiffImagePlugin').disabled = True


class Distribution:
    '''
    classdocs
    '''

    def __init__(self,
                 args
                 ):
        '''
        Constructor
        '''
        # Processing dirpath
        self.dirpath = args.input
        # Labels and values
        self.labels = {}
        # Extra verify
        self.verifyAnnotations = args.verifyAnnotations
        # Extra verify
        self.verifyImages = args.verifyImages
        # Is showcase enabled
        self.isShowcase = args.showcase
        # Statistics dataframe of all annotations
        self.distribution = {
            'Directory': [],
            'File': [],
            'Width': [],
            'Height': []
        }
        # Rename class x to y
        self.rename = None
        if (args.rename is not None):
            parts = args.rename.split(':')
            if (len(parts) == 2):
                self.rename = {int(parts[0]): int(parts[1])}

        # Call main processing function
        self.Process(self.dirpath)

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
                    self.AddAnnotationToDistribution(dirpath, filepath, entry)

                # TODO verify annotations

                # Do extra verify of images
                if (self.verifyImages is True):
                    # If exists image
                    if (IsExistsImage(dirpath+filepath) is True):
                        path = GetImageFilepath(dirpath+filepath)

                        # Check file size
                        if (os.stat(path).st_size == 0):
                            logging.error('Image %s size equal to zero!', path)
                        else:
                            try:
                                # Check if image is readable
                                v_image = Image.open(path)
                                try:
                                    # Check internal content
                                    v_image.verify()
                                except:
                                    logging.error('Image %s damaged!', path)
                            except:
                                logging.error('Image %s not openable!', path)
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

    def AddAnnotationToDistribution(self, directory, filename, entry):
        '''Store entry.'''
        # Extract label from annotation
        label, bbox = entry

        # Add label to distribution keys
        if (label not in self.distribution.keys()):
            self.distribution[label] = []
            # Get current state distribution length
            length = len(self.distribution['File'])
            # Insert missing entries as None or zero
            self.distribution[label] += length * [0]

        # Store entry in distribution
        self.distribution['Directory'].append(directory)
        self.distribution['File'].append(filename)
        self.distribution['Width'].append(GetWidth(bbox))
        self.distribution['Height'].append(GetHeight(bbox))
        self.distribution[label].append(1)
        # Update rest of entries with zero value.
        for key in self.distribution.keys():
            if key not in ['File', 'Directory', 'Width', 'Height', label]:
                self.distribution[key].append(0)

        # Sum & count labels occurencies
        if (label in self.labels.keys()):
            self.labels[label] += 1
        else:
            self.labels[label] = 1

    def Save(self, dirpath):
        ''' Save & plot distribution.'''
        dirpath = FixPath(dirpath)

        # Save distribution as .csv
        path = dirpath+'filelist.csv'
        df = pd.DataFrame.from_dict(self.distribution)
        df.to_csv(path, sep=';', decimal=',', index=False)
        logging.info('(Distribution) Created `%s`.', path)

        # Decorate as distribution showcase
        if (self.isShowcase):
            DecoratorDistributionShowcase(
                subdirectory='Informations').Decorate(df)

        # Save distribution summary as .csv
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
