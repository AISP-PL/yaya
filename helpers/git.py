'''
Created on 3 gru 2020

@author: spasz
'''
import subprocess
from datetime import datetime


def GetGitRev():
    '''Return current git revision.'''
    return subprocess.check_output(['git', 'describe', '--tags']).strip().decode('utf-8')


def GetGitBranchRev():
    '''
        Return current git revision with branch name.
        - fix for branches with slash/backslash
    '''
    branchName = subprocess.check_output(
        ['git', 'rev-parse', '--abbrev-ref', 'HEAD']).strip().decode('utf-8')
    branchName = branchName.replace('/', '.').replace('\\', '.')
    return subprocess.check_output(['git', 'describe', '--tags']).strip().decode('utf-8') + '-' + branchName


def GetYearWeekRev():
    '''Return current YearWeek revision - ubuntu schema.'''
    now = datetime.now()
    return now.strftime('%y%Vv%w')


def GetYearWeekTimeRev():
    '''Return current YearWeek revision - ubuntu schema.'''
    now = datetime.now()
    return now.strftime('%y%Vv%w. %H:%M:%S')
