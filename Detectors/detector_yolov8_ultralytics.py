import hashlib
import logging
import os
from shutil import copyfile
from typing import Any

import numpy as np
from ultralytics import YOLO  # type: ignore

from Detectors.common.Detector import Detector, NmsMethod
from Detectors.common.image_strategy import ImageStrategy
from helpers.aisp_typing import NumpyArray
from helpers.boxes import ToRelative

logger = logging.getLogger(__name__)


class DetectorYolov8(Detector):
    """YOLOv8 detector class."""

    def __init__(
        self,
        weights_path: str,
        names_path: str,
        imageStrategy: ImageStrategy = ImageStrategy.Rescale,
        gpu_id: int = 0,
    ) -> None:
        """
        Constructor
        """
        Detector.__init__(self, gpuid=gpu_id, name="yolov8")
        # GPU used
        self.gpuid: str | int = gpu_id
        # Weights file path
        self.weights_path = weights_path
        # Data file path
        self.names_path = names_path

        # Network configuration
        # ---------------------
        # Network pointer
        self.net = None

        # Network size
        self.netSize = 640

        config: dict[str, Any] = {}
        # Confidence threshold
        self.confidence = 0.20
        # NMS threshold
        self.nms_thresh = 0.45
        # Model task
        self.task = config.get("ultralytics", {}).get("task", "detect")
        # Half precision
        self.half_precision = config.get("ultralytics", {}).get("half_precision", False)
        # TensortRT
        self.use_tensorrt = config.get("ultralytics", {}).get("use_tensorrt", False)
        # Force CPU : Check
        if config.get("force_cpu", False):
            logger.warning("Forcing CPU usage for YOLOv8 detector!")
            self.gpuid = "cpu"
            self.use_tensorrt = False

        # Pre-Read and strip all labels
        with open(self.names_path) as f:
            self.classes = f.readlines()
        self.classes = list(map(str.strip, self.classes))  # strip names

        # Info : Logging
        logger.info(
            "YOLOv8 Detector created with task=%s weights=%s, names=%s",
            self.task,
            self.weights_path,
            self.names_path,
        )
        logger.info(
            "YOLOv8 Detector created with confidence=%2.2f, nms=%2.2f, half_precision=%d, use_tensorrt=%d",
            self.confidence,
            self.nms_thresh,
            self.half_precision,
            self.use_tensorrt,
        )

    def __del__(self) -> None:
        """Destructor."""
        # Free memory
        if self.net is not None:
            del self.net
            self.net = None
        # Free GPU memory

    def is_initialized(self) -> bool:
        """Return True if detector is initialized."""
        return self.net is not None

    def _load_create_tensortt(self, batch_size: int) -> YOLO:
        """
        Load and create TensorRT model

        Parameters
        ----------
        batch_size : int
            Batch size for TensorRT model

        Returns
        -------
        YOLO
            YOLOv8 model - TensorRT or YOLOv8
        """
        # Check : TensorRT usage enabled
        if not self.use_tensorrt:
            logger.info("TensorRT usage disabled. Using YOLOv8 model.")
            return YOLO(self.weights_path, verbose=False, task=self.task)

        # Check : Temp directory exists
        temp_dir = "temp"
        os.makedirs(temp_dir, exist_ok=True)

        # Paths : Create
        base = os.path.splitext(os.path.basename(self.weights_path))[0]
        engine_path = os.path.join(temp_dir, f"{base}_b{batch_size}.engine")
        checksum_path = os.path.join(temp_dir, f"{base}_b{batch_size}.checksum")

        # CheckSUM : Calculate for weights
        with open(self.weights_path, "rb") as f:
            checksum = hashlib.sha256(f.read())
            # Checksum : Calculate also batch size
            checksum.update(str(batch_size).encode("utf-8"))
            # Checksum : As SHA256 string
            new_checksum = checksum.hexdigest()

        # Check : Previous checksum == new checksum
        if os.path.exists(engine_path) and os.path.exists(checksum_path):
            with open(checksum_path) as cf:
                old_checksum = cf.read().strip()

            if new_checksum == old_checksum:
                logger.info("Loading existing TensorRT model %s.", engine_path)
                return YOLO(engine_path, verbose=False, task=self.task)

            logger.warning(
                "Found new weights for model! Checksum %s!=%s differs for %s.",
                old_checksum,
                new_checksum,
                engine_path,
            )

        # Model : Create and export
        logger.info(
            "TensorRT model not found or outdated. Creating model %s. It could take some time...",
            engine_path,
        )
        model = YOLO(self.weights_path, verbose=False, task=self.task)
        model.export(
            format="tensorrt",
            device=str(self.gpuid),
            half=self.half_precision,
            batch=batch_size,
        )

        # Check: Exported .onnx model exists
        exported_path_onnx = os.path.splitext(self.weights_path)[0] + ".onnx"
        if os.path.exists(exported_path_onnx):
            # remove old .onnx model
            os.remove(exported_path_onnx)

        # Copy exported model to engine path
        exported_path = os.path.splitext(self.weights_path)[0] + ".engine"
        copyfile(exported_path, engine_path)

        # Checksum : Save new checksum
        with open(checksum_path, "w") as cf:
            cf.write(new_checksum)

        logger.info("Loading new TensorRT model %s.", engine_path)
        return YOLO(engine_path, verbose=False)

    def Init(self) -> None:
        """Init call with other arguments."""
        return self.init(batch_size=1)

    def init(self, batch_size: int = 1) -> None:
        """Init call with other arguments."""
        # Check : Network weights should exists
        if self.weights_path is None:
            raise Exception("Network weights not specified!")

        # Check : Network weights should be larger > 1MiB
        if os.path.getsize(self.weights_path) < 1024 * 1024:
            raise Exception(
                "Network weights are too small! Have you installed git-LFS?"
            )

        # YOLO net, labels, cfg
        try:
            self.net = self._load_create_tensortt(batch_size)
        except Exception as e:
            raise Exception("Failed to load network!") from e

        # Logging
        logger.info(
            "Created network yolov8 has been initialized with %u classes.",
            len(self.classes),
        )

        if self.gpuid == "cpu":
            logger.warning("Model is running on CPU!")
        else:
            logger.info("GPU used : ID%s", str(self.gpuid))

    def open_stream(self, width: int, height: int, fps: float) -> None:
        """Open stream with stream details."""

    def detect(
        self,
        frame_number: int,
        confidence: float,
        nms_thresh: float,
        frame: NumpyArray,
    ) -> list[tuple]:
        """Detect objects in given frame"""
        # Image : Check
        if frame.size == 0:
            logger.error("(Detector) Image is empty!")
            return []

        imwidth, imheight = frame.shape[1], frame.shape[0]

        # Check : Image is valid
        if (imwidth == 0) or (imheight == 0):
            return []

        # Copy image to darknet image
        # YOLO detections format as np.ndarray
        # [[x1, y1, x2, y2, confidence, class_no], [...] ...]
        if self.net is None:
            logger.error("(Detector) Network is not initialized!")
            return []

        detections = self.net.predict(
            source=frame,
            conf=confidence,
            iou=nms_thresh,
            device=str(self.gpuid),
            half=self.half_precision,
            verbose=False,
        )

        # Check : Empty
        if len(detections) == 0:
            return []

        ultralytics_results = detections[0]
        class_id = ultralytics_results.boxes.cls.cpu().numpy().astype(int)
        xyxy = ultralytics_results.boxes.xyxy.cpu().numpy()
        confidence = ultralytics_results.boxes.conf.cpu().numpy()
        return self.ToDetections(boxes=xyxy, scores=confidence, classids=class_id)

    def Detect(
        self,
        frame: NumpyArray,
        confidence: float = 0.5,
        nms_thresh: float = 0.45,
        boxRelative: bool = False,
        nmsMethod: NmsMethod = NmsMethod.Nms,
        image_strategy: ImageStrategy = ImageStrategy.Rescale,
    ) -> list[tuple]:
        """Detect objects in given image"""
        boundaryHeight, boundaryWidth = frame.shape[0], frame.shape[1]

        detections = self.detect(
            frame_number=0, confidence=confidence, nms_thresh=nms_thresh, frame=frame
        )

        # Change box coordinates to rectangle
        if boxRelative is True:
            h, w = boundaryHeight, boundaryWidth
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
