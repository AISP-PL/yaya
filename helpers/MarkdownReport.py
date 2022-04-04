'''
Created on 10 lut 2021

@author: spasz
'''
import time
import logging
import os
from helpers.git import GetYearWeekTimeRev, GetGitBranchRev
from helpers.files import FixPath


class MarkdownReport:
    '''
    classdocs
    '''

    def __init__(self, filepath):
        '''
        Constructor
        '''
        # Path for newly created report
        self.reportPath = filepath
        # Start time of report
        self.reportStartTime = None
        # Initial section number
        self.sectionNumber = 0
        # Initial section number
        self.subSectionNumber = 0
        # Number of entries inside report
        self.reportEntries = 0

    def Begin(self, title='Report'):
        ''' Start report.'''
        # Save start time
        self.reportStartTime = time.time()

        # Write report header only if file not exists
        if (not os.path.exists(self.reportPath)):
            with open(self.reportPath, 'w') as file:
                file.write('# %s\n---------------\n\n' % title)
                # Add Git tag + hash
                file.write('%s.\n' % GetGitBranchRev())
                # Add YW revision
                file.write('%s.\n' % GetYearWeekTimeRev())
                file.write('\n\n')

    def AddText(self, text):
        ''' Add raw text.'''
        with open(self.reportPath, 'a+') as file:
            file.write(text)

    def AddTextline(self, text):
        ''' Add raw textline.'''
        with open(self.reportPath, 'a+') as file:
            file.write(text+'\n')

    def AddDataframe(self, df):
        ''' Add raw textline.'''
        with open(self.reportPath, 'a+') as file:
            file.write(df.to_markdown()+'\n\n')

    def AddListItem(self, text):
        ''' Add list item.'''
        with open(self.reportPath, 'a+') as file:
            file.write('* '+text+'\n')

    def AddImage(self, path, description=''):
        ''' Add raw text.'''
        with open(self.reportPath, 'a+') as file:
            file.write('![%s](%s)\n' % (description, path))
            file.write(
                '\n<div style="text-align:center;">Obraz : %s</div>\n' % (description))
            file.write('\n\n')

    def AddTable(self, df):
        ''' Add raw text.'''
        with open(self.reportPath, 'a+') as file:
            file.write(df.to_markdown())
            file.write('\n')

    def AddLineSeparator(self):
        ''' Adds line separator.'''
        with open(self.reportPath, 'a+') as file:
            file.write('\n---\n\n')

    def AddEmptyLine(self):
        ''' Adds line separator.'''
        with open(self.reportPath, 'a+') as file:
            file.write('\n\n')

    def AddSection(self, text):
        ''' Adds section with name and numbering.'''
        # Set numbers
        self.sectionNumber += 1
        self.subSectionNumber = 0
        # Write
        with open(self.reportPath, 'a+') as file:
            file.write('# %u. %s\n' % (self.sectionNumber, text))

    def AddSubSection(self, text):
        ''' Adds sub section with name and numbering.'''
        # Set numbers
        self.subSectionNumber += 1
        # Write
        with open(self.reportPath, 'a+') as file:
            file.write('## %u.%u %s\n' %
                       (self.sectionNumber, self.subSectionNumber, text))

    def AddSubSubSection(self, text):
        ''' Adds sub section with name and numbering.'''
        # Write
        with open(self.reportPath, 'a+') as file:
            file.write('### %s\n' % (text))

    def AddEntry(self, filepath, text):
        ''' Add single report entry.'''

        # Write informations to report output file
        with open(self.reportPath, 'a+') as file:
            file.write('## %s\n' % filepath)
            file.write(text)
            file.write('\n\n')
            self.reportEntries += 1

    def End(self, text=''):
        ''' End of report.'''
        # Write summary if any entries
        if (self.reportEntries != 0):
            # Calculate summary data
            duration = time.time() - self.reportStartTime
            # Write summary
            with open(self.reportPath, 'a+') as file:
                file.write('# Report end.\n---------------\n')
                file.write(text)
                file.write('Duration **%us** for **%u files**. Time per file **%2.2fs**.' %
                           (duration, self.reportEntries, duration/self.reportEntries))
                logging.error('Duration %us for %u files. Time per file %2.2fs.',
                              duration, self.reportEntries, duration/self.reportEntries)
