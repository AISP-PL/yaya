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


def mAP(annotations, detections, minConfidence=0.5, minIOU=0.5):
    '''
        @TODO not implemented yet real mAP,
        temporary metric used instead.

        @param expected annotations
        @param detected annotations
    '''
    # Best mAP for no annotations
    if (annotations is None) or (len(annotations) == 0):
        return 1.0

    # Worst mAP for no detections
    if (detections is None) or (len(detections) == 0):
        return 0.0

    # 1. Drop detections with (confidence < minConfidence)
    detections = [item for item in detections if (
        item.confidence > minConfidence)]

    # True positives
    TP = 0
    # False positives
    FP = 0
    # True negatives
    TN = 0
    # False negatives
    FN = 0

    # 2. Calculate all IOU matrix.
    for annotation in annotations:
        # For each expected bbox score 1 for TruePositive
        # and score 0.5 for FalsePositive with threshold minIOU.
        matches = []
        for detection in detections:
            iou = MetricIOU(annotation.box, detection.box)
            if (iou > minIOU):
                matches.append((iou, detection))

        matches = sorted(matches, key=lambda x: x[0], reverse=True)

        # Check if matches has TP or FP or other.
        if (len(matches)):
            # Check only first match.
            iou, detection = matches[0]
            # Label and GroundTruth.
            if (detection.classNumber == annotation.classNumber):
                TP += 1
            # Not Label and GroundTruth.
            else:
                TN += 1
        # Not Label and not GroundTruth
        else:
            FN += 1

    # 4. Calculate TruePositives / ALL.
    return TP / len(annotations)
