'''
Created on 25 cze 2021

@author: spasz
'''
import os
import pandas as pd
from helpers.files import FixPath, GetExtension


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

        df = pd.DataFrame({'Labels': [key for key in self.labels.keys()],
                           'Counts': [key for key in self.labels.values()]})
        df = df.sort_values(by=['Labels'])
        df.to_csv(dirpath+'distribution.csv',
                  sep=';', decimal=',', index=False)
