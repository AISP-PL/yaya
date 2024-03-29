"""
    Class representing the YOLO detector for the world

"""

import logging
from collections import OrderedDict

import numpy as np
from inference.models.yolo_world import YOLOWorld

from Detectors.common.Detector import Detector, NmsMethod
from Detectors.common.image_strategy import ImageStrategy
from helpers.boxes import ToRelative, to_xyxy


class DetectorYOLOWorld(Detector):
    """
    YOLO World detector class.
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__(gpuid=0, id=0, name="YOLO World")
        # Load model
        self.model = YOLOWorld(model_id="yolo_world/l")

        # Ontology of labels
        self.ontology: OrderedDict[str, str] = OrderedDict()

        # logging
        logging.info("(YoloWorld) Loaded YOLO World model")

    def set_ontology(self, ontology: dict[str, str]):
        """Set ontology for detector"""
        self.ontology = OrderedDict()

        # Keys : Add and validate
        for key in ontology:
            # Check, if key is empty
            if (key is None) or len(key) == 0:
                logging.warning("Empty key %s in ontology", key)
                continue

            value = ontology[key]
            # Check, value is empty
            if (value is None) or len(value) == 0:
                logging.warning("Empty value %s in ontology", value)
                continue

            key = key.strip()
            value = value.strip()
            self.ontology[key] = value

        self.classes = self.ontology_labels

    @property
    def prompt_labels(self) -> list[str]:
        """Get prompt labels for detector"""
        return list(self.ontology.keys())

    @property
    def ontology_labels(self) -> list[str]:
        """Get ontology labels for detector"""
        return list(self.ontology.values())

    def Detect(
        self,
        frame: np.array,
        confidence: float = 0.1,
        nms_thresh: float = 0.45,
        boxRelative: bool = False,
        nmsMethod: NmsMethod = NmsMethod.Nms,
        image_strategy: ImageStrategy = ImageStrategy.Rescale,
    ):
        """Detect objects in given image"""

        imheight, imwidth, _ = frame.shape

        det_confidence = max(0.001, confidence)

        self.model.set_classes(self.prompt_labels)
        results = self.model.infer(frame, confidence=det_confidence)

        # Change results to list of detections
        detections = [
            (
                self.ontology[prediction.class_name],
                prediction.confidence,
                to_xyxy(
                    [prediction.x, prediction.y, prediction.width, prediction.height]
                ),
            )
            for prediction in results.predictions
        ]

        # Change box coordinates to rectangle
        if boxRelative is True:
            h, w = imheight, imwidth
            for i, d in enumerate(detections):
                className, conf, box = d
                # Correct (-x, -y) value to fit inside box
                x1, y1, x2, y2 = box
                x1 = max(0, min(x1, w))
                x2 = max(0, min(x2, w))
                y1 = max(0, min(y1, h))
                y2 = max(0, min(y2, h))
                box = x1, y1, x2, y2
                # Change to relative
                detections[i] = (className, conf, ToRelative(box, w, h))

        return detections
