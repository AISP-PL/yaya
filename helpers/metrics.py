'''
Created on 15 wrz 2020

@author: spasz
'''

import math
from . import boxes
from numba import njit
from helpers import prefilters


@njit(cache=True)
def MetricIOU(box1, box2):
    ''' Calculates metric.'''
    area1 = boxes.GetArea(box1)
    area2 = boxes.GetArea(box2)
    intersection = boxes.GetIntersectionArea(box1, box2)
    if (intersection != 0):
        return intersection / (area1+area2-intersection)
    return 0


def dDeficit(annotations, detections, minConfidence=0.5):
    '''
        Detections deficit +/-.
        - positive = to few detections,
        - negative = to many detctions,

        @param expected annotations
        @param detected annotations
    '''
    # 1. Drop detections with (confidence < minConfidence)
    detections = [item for item in detections if (
        item.confidence > minConfidence)]

    # Filter by IOU>=0.75 with itself.
    detections = prefilters.FilterIOUbyConfidence(detections, detections)

    return len(annotations) - len(detections)


def dSurplus(annotations, detections, minConfidence=0.5):
    '''
        Detections surplus +/-.
        - positive = to many detections,
        - negative = to few detctions,

        @param expected annotations
        @param detected annotations
    '''
    # 1. Drop detections with (confidence < minConfidence)
    detections = [item for item in detections if (
        item.confidence > minConfidence)]

    # Filter by IOU>=0.75 with itself.
    detections = prefilters.FilterIOUbyConfidence(detections, detections)

    return len(detections) - len(annotations)


def EvaluateMetrics(annotations, detections, minConfidence=0.5, minIOU=0.5):
    '''
        Definition of terms:
            True Positive (TP) — Correct detection made by the model.
            False Positive (FP) — Incorrect detection made by the detector.
            False Negative (FN) — A Ground-truth missed (not detected) by the object detector.
            True Negative (TN) —This is backgound region correctly not detected by the model.
        This metric is not used in object detection because such regions are not explicitly annotated when preparing the annotations.

        @param expected annotations
        @param detected annotations
    '''
    # No annotations results.
    if (annotations is None) or (len(annotations) == 0):
        return len(detections), 0, 0, len(detections), 0

    # No detections result.
    if (detections is None) or (len(detections) == 0):
        return 0, len(annotations), 0, 0, len(detections)

    # 1. Drop detections with (confidence < minConfidence)
    detections = [item for item in detections if (
        item.confidence > minConfidence)]

    # Annotation with Detection => TP or FN
    annotationsMatched = []
    # Annotation lonely. => FN
    annotationsUnmatched = []
    # Detection lonely. => FP
    detectionsUnmatched = []

    # For all annotations
    for annotation in annotations:
        # 1. Calculate all possibilities (detections)
        possibilities = [(MetricIOU(annotation.box, detection.box), detection)
                         for detection in detections]
        # Sort possibilities by IOU
        possibilities = sorted(possibilities, key=lambda x: x[0], reverse=True)
        # Check first(biggest IOU) possibility
        if (len(possibilities) and (possibilities[0][0] >= minIOU)):
            _iou, detection = possibilities[0]
            annotationsMatched.append((annotation, detection))
            detections.remove(detection)
        # Otherwise not matched
        else:
            annotationsUnmatched.append(annotation)

    # Detections unmatched are detections left in list.
    detectionsUnmatched = detections

    # True positives
    TP = len(annotationsMatched)
    # False positives
    FP = len(detectionsUnmatched)
    # False negatives
    FN = len(annotationsUnmatched)
    # Labels matched annotations (TP)
    LTP = sum(1 if (annotation.classNumber == detection.classNumber)
              else 0 for annotation, detection in annotationsMatched)
    # Labels unmatched annotations (N-LTP)
    LTN = len(annotations) - LTP

    # 4. Calculate TruePositives / ALL.
    return TP, FP, FN, LTP, LTN


def Precision(TP, FP):
    ''' Returns metric.'''
    if ((TP+FP) == 0):
        return 0

    return TP/(TP+FP)


def Recall(TP, FN):
    ''' Returns metric.'''
    if ((TP+FN) == 0):
        return 0

    return TP/(TP+FN)


def mAP(TP, length):
    ''' Returns metric.'''
    return TP/length
