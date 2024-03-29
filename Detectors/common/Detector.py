"""
Created on 23 lis 2020

@author: spasz
"""

import logging
from enum import Enum

import numpy as np

from Detectors.common.image_strategy import ImageStrategy
from Gui.drawing import DrawDetections
from helpers.ensemble_boxes_nms import nms, soft_nms
from helpers.ensemble_boxes_nmw import non_maximum_weighted
from helpers.ensemble_boxes_wbf import weighted_boxes_fusion


class NmsMethod(str, Enum):
    """Different NMS methods."""

    Nms = "Nms"
    SoftNms = "SoftNms"
    NmWeighted = "NmWeighted"
    WeightedBoxFusion = "WeightedBoxFusion"


class Detector:
    """
    Detector base class.
    """

    def __init__(self, gpuid=0, id=255, name=""):
        """
        Constructor
        """
        # Detector id
        self.id = id
        # GPU id for multiple gpus
        self.gpuid = gpuid
        # Detector name
        self.name = name
        # List of detector classes/labels
        self.classes = []
        # Colors of labels
        self.colors = []

        logging.debug("(Detector) Created %u.%s!", self.id, self.name)

    @property
    def details_str(self) -> str:
        return f"{self.__class__.__name__}"

    def Init(self):
        """Init call with other arguments."""
        # Default implementation

    def Close(self):
        """Called after processing whole video."""
        # Not implemented

    def GetDetector(self):
        """Return myself - virtual."""
        return self

    def Detect(
        self,
        frame: np.array,
        confidence: float = 0.5,
        nms_thresh: float = 0.45,
        boxRelative: bool = False,
        nmsMethod: NmsMethod = NmsMethod.Nms,
        image_strategy: ImageStrategy = ImageStrategy.Rescale,
    ):
        """Detect objects in given image"""
        return []

    @staticmethod
    def EnsembleBoxes(
        boxes,
        scores,
        classids,
        nmsMethod: NmsMethod = NmsMethod.Nms,
        iou_thresh=0.45,
        conf_thresh=0.5,
    ) -> tuple:
        """Ensbmle boxes using given method."""
        if nmsMethod == NmsMethod.Nms:
            return nms([boxes], [scores], [classids], iou_thr=iou_thresh)
        elif nmsMethod == NmsMethod.SoftNms:
            return soft_nms(
                [boxes], [scores], [classids], iou_thr=iou_thresh, thresh=conf_thresh
            )
        elif nmsMethod == NmsMethod.NmWeighted:
            npboxes, npscores, npclassids = non_maximum_weighted(
                [boxes],
                [scores],
                [classids],
                iou_thr=iou_thresh,
                skip_box_thr=conf_thresh,
            )
            return npboxes.tolist(), npscores.tolist(), npclassids.tolist()

        elif nmsMethod == NmsMethod.WeightedBoxFusion:
            return weighted_boxes_fusion(
                [boxes],
                [scores],
                [classids],
                iou_thr=iou_thresh,
                skip_box_thr=conf_thresh,
            )

    def ToDetections(
        self, boxes: list, scores: list[float], classids: list[int]
    ) -> list:
        """Zip together to sinigle tuples list."""
        return [
            (self.classes[int(classid)], 100 * score, box)
            for box, score, classid in zip(boxes, scores, classids)
        ]

    def GetName(self):
        """Returns detector name."""
        return self.name

    def GetID(self):
        """Returns detector class id."""
        return self.id

    def GetWidth(self):
        """Returns network image width."""
        return 0

    def GetHeight(self):
        """Returns network image height."""
        return 0

    def Draw(self, image, detections):
        """Draw all boxes on image"""
        return DrawDetections(image, detections, self.colors)

    def IsClassesAllowed(self, classes):
        """True if classes names are allowed
        within detector."""
        return set(classes).issubset(self.classes)

    def GetClassNames(self):
        """Returns all interesing us class names."""
        return self.classes

    def GetClassNumber(self, label: str) -> int:
        """Return number of label."""
        if self.classes is None:
            return -1

        if label not in self.classes:
            return -1

        return self.classes.index(label)
