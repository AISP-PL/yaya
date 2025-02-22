"""
Created on 15 wrz 2020

@author: spasz
"""

from dataclasses import dataclass, field

from engine.annote import Annote, AnnoteEvaluation
from helpers import prefilters

from . import boxes


@dataclass
class Metrics:
    """List of evaluated metrics"""

    # Number of all annotations
    All: int = field(init=True, default=0)
    # Average width of all annotations
    AvgWidth: float = field(init=True, default=-1.0)
    # Average height of all annotations
    AvgHeight: float = field(init=True, default=-1.0)
    # Average of best IOU of all annotations
    iou_avg: float = field(init=True, default=0.0)
    # Overallping IOU (rest of all detections)
    overlapping_iou: float = field(init=True, default=0.0)
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
    # List of all detections
    detections: list = field(init=True, default_factory=list)
    # List of new detections
    new_detections: list = field(init=True, default_factory=list)
    # List of matched pairs (annotation, detection)
    matches: list = field(init=True, default_factory=list)

    def __post_init__(self):
        """Post initiliatizaton."""

    @property
    def detections_confidence(self) -> float:
        """Returns confidence ."""
        if len(self.detections) == 0:
            return 0

        return sum([item.confidence for item in self.detections]) / len(self.detections)

    @property
    def detections_confidence_min(self) -> float:
        """Returns list of confidence values."""
        if len(self.detections) == 0:
            return 0

        return min([item.confidence for item in self.detections])

    @property
    def detections_confidence_max(self) -> float:
        """Returns list of confidence values."""
        if len(self.detections) == 0:
            return 0

        return max([item.confidence for item in self.detections])

    @property
    def matches_confidence(self) -> float:
        """Returns confidence ."""
        if len(self.matches) == 0:
            return 0

        return sum(
            [detection.confidence for annotation, detection in self.matches]
        ) / len(self.matches)

    @property
    def matches_confidence_min(self) -> float:
        """Returns list of confidence values."""
        if len(self.matches) == 0:
            return 0

        return min([detection.confidence for annotation, detection in self.matches])

    @property
    def matches_confidence_max(self) -> float:
        """Returns list of confidence values."""
        if len(self.matches) == 0:
            return 0

        return max([detection.confidence for annotation, detection in self.matches])

    @property
    def AvgSize(self) -> float:
        """Returns metric."""
        return self.AvgWidth * self.AvgHeight

    @property
    def correct(self) -> float:
        """Returns % of correct detections."""
        # Check : No annotations, then everything is correct.
        if self.All == 0:
            return 100

        return 100 * self.LTP / self.All

    @property
    def correct_bboxes(self) -> float:
        """Returns % of correct detections."""
        if self.All == 0:
            return 0

        return 100 * self.TP / self.All

    @property
    def precision(self):
        """Returns metric."""
        if (self.TP + self.FP) == 0:
            return 0

        return self.TP / (self.TP + self.FP)

    @property
    def recall(self) -> float:
        """Returns metric."""
        if (self.TP + self.FN) == 0:
            return 0

        return self.TP / (self.TP + self.FN)

    @property
    def mAP(self):
        """Returns metric."""
        return self.TP / self.All


def dDeficit(annotations, detections, minConfidence=0.5):
    """
    Detections deficit +/-.
    - positive = to few detections,
    - negative = to many detctions,

    @param expected annotations
    @param detected annotations
    """
    # 1. Drop detections with (confidence < minConfidence)
    detections = [item for item in detections if (item.confidence > minConfidence)]

    # Filter by IOU>=0.75 with itself.
    detections = prefilters.filter_iou_by_confidence(detections, detections)

    return len(annotations) - len(detections)


def dSurplus(annotations, detections, minConfidence=0.5):
    """
    Detections surplus +/-.
    - positive = to many detections,
    - negative = to few detctions,

    @param expected annotations
    @param detected annotations
    """
    # 1. Drop detections with (confidence < minConfidence)
    detections = [item for item in detections if (item.confidence > minConfidence)]

    # Filter by IOU>=0.75 with itself.
    detections = prefilters.filter_iou_by_confidence(detections, detections)

    return len(detections) - len(annotations)


def EvaluateMetrics(
    annotations: list[Annote],
    detections: list[Annote],
    minConfidence: float = 0.5,
    minIOU: float = 0.5,
) -> Metrics:
    """
    Definition of terms:
        True Positive (TP) — Correct detection made by the model.
        False Positive (FP) — Incorrect detection made by the detector.
        False Negative (FN) — A Ground-truth missed (not detected) by the object detector.
        True Negative (TN) —This is backgound region correctly not detected by the model.
    This metric is not used in object detection because such regions are not explicitly annotated when preparing the annotations.

    @param expected annotations
    @param detected annotations
    """
    # Check : No annotations, then all detections as FP.
    if (annotations is None) or (len(annotations) == 0):
        return Metrics(
            FP=len(detections), new_detections=detections, detections=detections
        )

    # Check : No detections, all annotations as missed.
    if (detections is None) or (len(detections) == 0):
        return Metrics(All=len(annotations))

    # 0. Detections copy
    original_detections = detections.copy()

    # 1. Drop detections with (confidence < minConfidence)
    detections = [item for item in detections if (item.confidence > minConfidence)]

    # Metric : Annotations overlapping.
    # Calculate total sum of all IOU overlapings with other annotations.
    overlapping_iou_avg: float = 0.0
    for i, annotation in enumerate(annotations):
        # Calculate IOU with all other annotations.
        annotation_ious_sum: float = 0.0
        for j, other in enumerate(annotations):
            if i == j:
                continue

            annotation_ious_sum += boxes.iou(annotation.box, other.box)

        # Sum of all IOU overlapiings with other annotations.
        overlapping_iou_avg += annotation_ious_sum / len(annotations)

    # Average of all IOU overlapiings with other annotations.
    overlapping_iou_avg /= len(annotations)

    # Annotation with Detection => TP or FN
    annotationsMatched = []
    # Annotation lonely. => FN
    annotationsUnmatched = []
    # Detection lonely. => FP
    detectionsUnmatched = []
    # List of all best IOUs for all annotations
    ious_best: list[float] = []

    # For all annotations
    for annotation in annotations:
        # Check : Any detections
        if len(detections) == 0:
            annotation.SetEvalution(AnnoteEvaluation.FalseNegative, iou=0, confidence=0)
            annotationsUnmatched.append(annotation)
            ious_best.append(0)
            continue

        # 1. IOU (annotations, detections)
        possibilities: list[tuple[float, Annote]] = [
            (boxes.iou(annotation.box, detection.box), detection)
            for detection in detections
        ]

        # Sort and get best
        possibilities = sorted(possibilities, key=lambda x: x[0], reverse=True)
        iou_best, detection = possibilities[0]

        # Check : Not matched
        if iou_best < minIOU:
            annotation.SetEvalution(AnnoteEvaluation.FalseNegative, iou=0, confidence=0)
            annotationsUnmatched.append(annotation)
            ious_best.append(0)
            continue

        # Match : Box and class number
        if annotation.classNumber == detection.classNumber:
            annotation.SetEvalution(
                AnnoteEvaluation.TruePositiveLabel,
                iou=iou_best,
                confidence=detection.confidence,
            )
        # Match : Box only
        else:
            annotation.SetEvalution(
                AnnoteEvaluation.TruePositive,
                iou=iou_best,
                confidence=detection.confidence,
            )

        annotationsMatched.append((annotation, detection))
        detections.remove(detection)
        ious_best.append(iou_best)

    # Detections unmatched are detections left in list.
    detectionsUnmatched = detections
    # For view : Filter by IOU internal with same annotes and also with txt annotes.
    detectionsUnmatched = prefilters.filter_iou_by_confidence(
        detectionsUnmatched, annotations
    )

    # True positives // Annotations Bboxes matched
    TP = len(annotationsMatched)
    # False positives // Detections unmatched, new!
    FP = len(detectionsUnmatched)
    # False negatives // Annotations bboxes unmatched
    FN = len(annotationsUnmatched)

    # Labels properly matched annotations (TP) in %
    LTP = sum(
        1 if (annotation.classNumber == detection.classNumber) else 0
        for annotation, detection in annotationsMatched
    )

    # Get average width and height of annotations.
    avgWidth = sum([annotation.width for annotation in annotations]) / len(annotations)
    avgHeight = sum([annotation.height for annotation in annotations]) / len(
        annotations
    )

    return Metrics(
        All=len(annotations),
        AvgWidth=avgWidth,
        AvgHeight=avgHeight,
        iou_avg=sum(ious_best) / len(ious_best),
        overlapping_iou=overlapping_iou_avg,
        TP=TP,
        FP=FP,
        FN=FN,
        LTP=LTP,
        detections=original_detections,
        new_detections=detectionsUnmatched,
        matches=annotationsMatched,
    )
