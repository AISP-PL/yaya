'''
Created on 15 wrz 2020

@author: spasz
'''

from dataclasses import dataclass, field
from . import boxes
from helpers import prefilters
from engine.annote import AnnoteEvaluation


@dataclass
class Metrics:
    ''' List of evaluated metrics '''
    # Number of all annotations
    All: int = field(init=True, default=0)
    # Average width of all annotations
    AvgWidth: float = field(init=True, default=0)
    # Average height of all annotations
    AvgHeight: float = field(init=True, default=0)
    # True postive validated annotations
    TP: int = field(init=True, default=0)
    # False positive validated annotations
    FP: int = field(init=True, default=0)
    # False negative validated annotations
    TN: int = field(init=True, default=0)
    # Label true positive
    FN: int = field(init=True, default=0)
    # Label true positive
    LTP: int = field(init=True, default=0)

    def __post_init__(self):
        ''' Post initiliatizaton.'''

    @property
    def AvgSize(self) -> float:
        ''' Returns metric.'''
        return self.AvgWidth * self.AvgHeight

    @property
    def correct(self) -> float:
        ''' Returns % of correct detections.'''
        if (self.All == 0):
            return 0

        return 100 * self.LTP / self.All

    @property
    def correct_bboxes(self) -> float:
        ''' Returns % of correct detections.'''
        if (self.All == 0):
            return 0

        return 100*self.TP / self.All

    @property
    def new_detections(self) -> int:
        ''' Newly detected bboxes'''
        return self.FP

    @property
    def precision(self):
        ''' Returns metric.'''
        if (self.TP + self.FP) == 0:
            return 0

        return self.TP/(self.TP+self.FP)

    @property
    def recall(self) -> float:
        ''' Returns metric.'''
        if ((self.TP+self.FN) == 0):
            return 0

        return self.TP/(self.TP+self.FN)

    @property
    def mAP(self):
        ''' Returns metric.'''
        return self.TP/self.All


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


def EvaluateMetrics(annotations: list,
                    detections: list,
                    minConfidence: float = 0.5,
                    minIOU: float = 0.5) -> tuple:
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
    # Check : No annotations, then all detections as FP.
    if (annotations is None) or (len(annotations) == 0):
        return Metrics(FP=len(detections))

    # Check : No detections, all annotations as missed.
    if (detections is None) or (len(detections) == 0):
        return Metrics(All=len(annotations))

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
            if (annotation.classNumber == detection.classNumber):
                annotation.SetEvalution(AnnoteEvaluation.TruePositiveLabel)
            else:
                annotation.SetEvalution(AnnoteEvaluation.TruePositive)
            annotationsMatched.append((annotation, detection))
            detections.remove(detection)
        # Otherwise not matched
        else:
            annotation.SetEvalution(AnnoteEvaluation.FalseNegative)
            annotationsUnmatched.append(annotation)

    # Detections unmatched are detections left in list.
    detectionsUnmatched = detections
    # For view : Filter by IOU internal with same annotes and also with txt annotes.
    detectionsUnmatched = prefilters.FilterIOUbyConfidence(detectionsUnmatched,
                                                           annotations)

    # True positives // Annotations Bboxes matched
    TP = len(annotationsMatched)
    # False positives // Detections unmatched, new!
    FP = len(detectionsUnmatched)
    # False negatives // Annotations bboxes unmatched
    FN = len(annotationsUnmatched)

    # Labels properly matched annotations (TP) in %
    LTP = sum(1 if (annotation.classNumber == detection.classNumber)
              else 0 for annotation, detection in annotationsMatched)

    # Get average width and height of annotations.
    avgWidth = sum(
        [annotation.width for annotation in annotations]) / len(annotations)
    avgHeight = sum(
        [annotation.height for annotation in annotations]) / len(annotations)

    return Metrics(All=len(annotations),
                   AvgWidth=avgWidth,
                   AvgHeight=avgHeight,
                   TP=TP,
                   FP=FP,
                   FN=FN,
                   LTP=LTP
                   )
