import os


def IsCuda():
    ''' Checks if GPU cuda is installed and working.'''
    if (os.system('nvcc --version') == 0):
        return True

    return False


def CreateDetector(detectorID=0, gpuID=0):
    ''' Creates detector.'''
