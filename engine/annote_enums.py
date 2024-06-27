from enum import Enum


class AnnoteAuthorType(Enum):
    """Annotation author type."""

    byHuman = 0
    byDetector = 1
    byHand = 2


class AnnoteEvaluation(Enum):
    """Annotation evalution."""

    noEvaluation = 0
    TruePositiveLabel = 1
    TruePositive = 2
    FalseNegative = 3


class AnnotatorType(str, Enum):
    """Annotator type."""

    Default = "Default"
    ConfidenceHeat = "ConfidenceHeat"
