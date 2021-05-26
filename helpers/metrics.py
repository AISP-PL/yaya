'''
Created on 15 wrz 2020

@author: spasz
'''

import math
from . import boxes
from numba import njit


@njit(cache=True)
def MetricIOU(box1, box2):
    ''' Calculates metric.'''
    area1 = boxes.GetArea(box1)
    area2 = boxes.GetArea(box2)
    intersection = boxes.GetIntersectionArea(box1, box2)
    if (intersection != 0):
        return intersection / (area1+area2-intersection)
    return 0
