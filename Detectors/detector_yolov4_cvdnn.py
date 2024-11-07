"""
YOLOv4 detector class using OpenCV DNN module.
"""

import logging
from typing import Optional, Sequence

import cv2
import numpy as np

from Detectors.common.Detector import NmsMethod, Detector
from Detectors.common.image_strategy import ImageStrategy
from helpers.boxes import ToRelative


def xlylwh_to_xyxy(bbox: Sequence[int]) -> tuple[int, int, int, int]:
    """
    Xtopleft, Ytopleft, W, H -> XMIN, YMIN, XMAX, YMAX
    """
    xtl, ytl, w, h = bbox

    xmin = xtl
    ymin = ytl
    xmax = xtl + w
    ymax = ytl + h

    return (xmin, ymin, xmax, ymax)


class DetectorCVDNN(Detector):
    """YOLOv4 detector class."""

    def __init__(
        self,
        cfgPath,
        weightPath,
        dataPath,
        namesPath,
        name="CVDNN",
        gpuID: int = 0,
        netWidth: int = 0,
        netHeight: int = 0,
    ):
        """
        Constructor
        """
        Detector.__init__(self, id=0, gpuid=0, name=name)
        # GPU used
        self.gpuid = gpuID
        # Configuration dictionary
        self.cfg_path = cfgPath
        # Weights file path
        self.weights_path = weightPath
        # Data file path
        self.data_path = dataPath
        # Names file path
        self.names_path = namesPath
        # Force cpue default yes
        self.force_cpu = True

        # Network configuration
        # ---------------------
        # Network pointer
        self.net: Optional[cv2.dnn.Net] = None
        # Model pointer
        self.model: Optional[cv2.dnn.DetectionModel] = None
        # Network width
        self.netWidth = netWidth
        # Network height
        self.netHeight = netHeight
        # Network layers list
        self.netLayers: Optional[tuple[str, ...]] = None

        # Pre-Read and strip all labels
        self.classes: list[str] = open(self.names_path, "r").read().splitlines()
        self.classes = list(map(str.strip, self.classes))  # strip names

        # Reused darknet image
        self.image = None
        # Reused darknet image properties
        self.imwidth = 0
        self.imheight = 0

    def __del__(self):
        """Destructor."""

    def is_initialized(self) -> bool:
        """Return True if detector is initialized."""
        return self.net is not None

    def __init_from_darknet(self) -> None:
        """Initialize network."""
        # Darknet : Load from darknet .cfg i .weights
        self.net = cv2.dnn.readNetFromDarknet(self.cfg_path, self.weights_path)

        # Get network input size
        with open(self.cfg_path, "r") as cfg_file:
            for line in cfg_file.readlines():
                if line.startswith("width"):
                    self.netWidth = int(line.strip().split("=")[1])
                if line.startswith("height"):
                    self.netHeight = int(line.strip().split("=")[1])

    def Init(self) -> None:
        """Init call with other arguments."""
        # Check : OpenCV using optimized version
        if not cv2.useOptimized():
            logging.warning("CV2 is not CPU optimized!")

        # Initialize network according to network type
        self.__init_from_darknet()

        # Check if network was loaded
        if self.net is None:
            raise ValueError("Failed to load network!")

        # GPU : Use cuda
        if not self.force_cpu:
            self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
            self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA_FP16)
        # Otherwise : Use CPU
        else:
            self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
            self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)

        # Logging network informations
        logging.info(
            "Created %ux%u network with %u classes.",
            self.netWidth,
            self.netHeight,
            len(self.classes),
        )

        # Get all network layers names
        self.netLayers = tuple(self.net.getLayerNames())
        # Get all network unconnected layers
        self.netOutLayers = self.net.getUnconnectedOutLayersNames()
        # Get detection model reference for network
        self.model = cv2.dnn_DetectionModel(self.net)  # type: ignore
        if self.model is None:
            raise ValueError("Failed to create detection model!")

        # Set input parameters for model
        self.model.setInputParams(
            size=(self.netWidth, self.netHeight), scale=1 / 255, swapRB=True
        )

        # Logging network output layers names.
        logging.info("Network output layers: %s", ",".join(self.netOutLayers))

        logging.info(
            "Created %ux%u network with %u classes.",
            self.netWidth,
            self.netHeight,
            len(self.classes),
        )
        logging.info("GPU used : ID%d", self.gpuid)

    def Detect(
        self,
        frame: np.array,
        confidence: float = 0.5,
        nms_thresh: float = 0.45,
        boxRelative: bool = False,
        nmsMethod: NmsMethod = NmsMethod.Nms,
        image_strategy: ImageStrategy = ImageStrategy.Rescale,
    ):
        """Detect objects in given frame"""
        # Image : Check
        if frame is None:
            logging.error("(Detector) Image is None!")
            return []

        # Network : Check
        if self.net is None or self.model is None:
            logging.error("(Detector) Network is not initialized!")
            return []

        # Image : Dimensions
        imwidth = frame.shape[1]
        imheight = frame.shape[0]

        # Check : Image is valid
        if (imwidth == 0) or (imheight == 0):
            return []

        # Frame : Swap BGR to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        yolo_classids, yolo_confidences, yolo_bboxes = self.model.detect(
            frame=frame_rgb, confThreshold=confidence, nmsThreshold=nms_thresh
        )

        # Check : Empty
        if len(yolo_bboxes) == 0:
            return []

        # As supervision : convert to supervision format
        # [xyxy array, classes array, and confidences array]
        yolo_xyxy = np.array([xlylwh_to_xyxy(bbox) for bbox in yolo_bboxes])

        detections = [
            (self.classes[class_id], 100 * confidence, tuple(xyxy.tolist()))
            for class_id, confidence, xyxy, in zip(
                yolo_classids, yolo_confidences, yolo_xyxy
            )
        ]

        # Change box coordinates to rectangle
        if boxRelative is True:
            h, w = imheight, imwidth
            for i, d in enumerate(detections):
                className, confidence, box = d
                # Correct (-x, -y) value to fit inside box
                x1, y1, x2, y2 = box
                x1 = max(0, min(x1, w))
                x2 = max(0, min(x2, w))
                y1 = max(0, min(y1, h))
                y2 = max(0, min(y2, h))
                box = x1, y1, x2, y2
                # Change to relative
                detections[i] = (className, confidence, ToRelative(box, w, h))

        return detections
