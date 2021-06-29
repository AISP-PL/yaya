'''
Created on 25 cze 2021

@author: spasz
'''
import os
import logging
import pandas as pd
from helpers.files import FixPath, GetExtension
import matplotlib.pyplot as plt
import matplotlib
from lib2to3.fixes.fix_paren import FixParen

matplotlib.use('Agg')
logging.getLogger('matplotlib.font_manager').disabled = True


class Distribution:
    '''
    classdocs
    '''

    def __init__(self, dirpath):
        '''
        Constructor
        '''
        # Processing dirpath
        self.dirpath = dirpath
        # Labels and values
        self.labels = {}

        self.Process(dirpath)

    def Process(self, dirpath):
        ''' Process files list.'''
        dirpath = FixPath(dirpath)
        # For every file
        for filepath in os.listdir(dirpath):
            # Check if annotation's
            if (GetExtension(filepath) == '.txt'):
                # Open annotations files
                with open(dirpath+filepath) as f:
                    # Parse every line
                    for line in f:
                        entry = self.__ReadYoloEntry(line)
                        if (entry is not None):
                            self.__AddEntryToDistribution(entry)

        logging.info('(Distribution) Processed distribution. Found:')
        logging.info(self.labels)

    def __ReadYoloEntry(self, line):
        '''Read oneline yolo entry.'''
        words = line.split()

        # Words length must be exactly 5
        if (len(words) != 5):
            return None

        # Return class number
        return int(words[0])

    def __AddEntryToDistribution(self, entry):
        '''Store entry.'''
        if (entry in self.labels.keys()):
            self.labels[entry] += 1
        else:
            self.labels[entry] = 1

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
        plt.yticks(ticks=range(0, max(df['Counts'].values), 1000))
        plt.xticks(ticks=range(len(df['Labels'])), rotation=45)

        # Save figure
        plt.savefig(dirpath+'distribution.png')
        logging.info('(Distribution) Created `%s`.',
                     dirpath+'distribution.png')
