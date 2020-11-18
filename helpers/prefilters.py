'''
Created on 18 lis 2020

@author: spasz
'''


def FilterIOUbyConfidence(annotations, maxIOU=0.8):
    '''
        Filter annotation if has bigger IOU > maxIOU.
        Annotation with bigger confidence stays!
    '''
