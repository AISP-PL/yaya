"""
    Detection namedtuple inheriting class with
    additional properties and methods.
"""

from dataclasses import dataclass, field

import numpy as np

# List of class names : Set by the detector
_class_names = []


def setup_detecor(class_names: list[str]):
    """Setup class names."""
    global _class_names
    _class_names = class_names


@dataclass
class Detection:
    """
    Detection (label, confidence, box) with all possibilities values, additional properties and methods.
    Stored as it is inside YOLO HEAD.

    Properties:
        label:   str label of the detection
        confidence: float confidence of the detection
        box:     tuple (x1, y1, x2, y2) of the detection

    """

    # YOLO bounding box
    xywh: list[float] = field(init=True)
    # Objectness
    objectness: float = field(init=True)
    # Class probabilities
    probabilities: list[float] = field(init=True)

    def as_tuple(self) -> tuple:
        """Return Detection as tuple"""
        return (self.xywh, self.confidence, self.class_label)

    @property
    def confidence(self) -> float:
        """Returns max confidence."""
        return max(self.probabilities)

    @property
    def class_id(self) -> int:
        """Returns class id."""
        return self.probabilities.index(max(self.probabilities))

    @property
    def class_label(self) -> float:
        """Returns class label."""
        index = self.probabilities.index(max(self.probabilities))
        return _class_names[index]

    @property
    def center(self):
        """Center of the box."""
        return self.xywh[:2]

    @property
    def width(self):
        """Width of the box."""
        return self.xywh[2]

    @property
    def height(self):
        """Height of the box."""
        return self.xywh[3]

    @property
    def area(self):
        """Area of the box."""
        return self.width * self.height
