"""
Created on 22 sie 2020

@author: spasz
"""

import logging
import os
from math import ceil
from typing import NamedTuple

import cv2
import numpy as np

from Detectors.common.Detector import Detector, NmsMethod
from Detectors.common.image_strategy import ImageStrategy
from Detectors.yolov4 import darknet
from helpers.boxes import ToRelative
from helpers.detections import tiles_detections_merge
from helpers.files import GetFilepath
from helpers.gpu import CudaDeviceLowestMemory
from helpers.images import GetFixedFitToBox


class ImageTile(NamedTuple):
    """Image tile object."""

    image: np.array
    offset_x: int
    offset_y: int


class DetectorYOLOv4(Detector):
    """
    classdocs
    """

    def __init__(
        self,
        cfgPath,
        weightPath,
        dataPath,
        name="YOLOv4",
        imageStrategy=None,
    ):
        """
        Constructor
        """
        Detector.__init__(self, id=0, gpuid=0, name=name)
        # Store yolo configuartion paths
        self.config = {
            "Config": cfgPath,
            "Weights": weightPath,
            "Names": dataPath,
        }
        # Network pointer
        self.net = None
        # Network width
        self.netWidth = 0
        # Network height
        self.netHeight = 0
        # Reused darknet image
        self.image = None
        # Reused darknet image properties
        self.imwidth = 0
        self.imheight = 0

        # Image strategy
        self.imageStrategy = imageStrategy
        if self.imageStrategy is None:
            self.imageStrategy = int(os.environ.get("DETECTORYOLOV4_STRATEGY", "0"))

        # List of colors matched with labels
        self.colors = []
        # Pre-Read and strip all labels
        self.classes = (
            open(GetFilepath(dataPath, dropExtension=True) + ".names")
            .read()
            .splitlines()
        )
        self.classes = list(map(str.strip, self.classes))  # strip names

        # Validate labels
        self.__validateLabels()

    def __del__(self):
        """Destructor."""
        # Free network image
        if self.image is not None:
            darknet.free_image(self.image)

        # Unload network from memory
        if self.net is not None:
            darknet.free_network_ptr(self.net)

    def __validateLabels(self):
        """Validated loaded labels."""
        # Check if last label is empty (could be because of \n)
        if (self.classes[-1] == "") or (len(self.classes[-1]) == 0):
            del self.classes[-1]
            logging.warning("(DetectorYOLOv4) Removed last empty label!")
        # Check labels integrity
        for c in self.classes:
            # Check for missing labels
            if len(c) == 0:
                logging.fatal("(DetectorYOLOv4) Missing label '%s' for class!", c)
                raise ValueError()

    def IsInitialized(self):
        """Return True if detector is initialized."""
        return self.net is not None

    def Init(self):
        """Init call with other arguments."""
        # GPU : Set lowest usage GPU, fallback to default
        gpu_id_lowest = CudaDeviceLowestMemory()
        if gpu_id_lowest is None:
            gpu_id_lowest = self.gpuid

        darknet.set_gpu(gpu_id_lowest)

        # YOLO net, labels, cfg
        self.net, self.classes, self.colors = darknet.load_network(
            self.config["Config"], self.config["Names"], self.config["Weights"]
        )

        # Get network  input (width and height)
        self.netWidth = darknet.network_width(self.net)
        self.netHeight = darknet.network_height(self.net)

        # Validate detector
        self.__validateLabels()

        logging.info(
            "(DetectorYOLOv4) Created %ux%u network with %u classes.",
            self.netWidth,
            self.netHeight,
            len(self.classes),
        )

    def GetWidth(self):
        """Returns network image width."""
        return self.netWidth

    def GetHeight(self):
        """Returns network image height."""
        return self.netHeight

    def detect_rescale(
        self,
        frame: np.array,
        confidence: float = 0.5,
        nms_thresh: float = 0.45,
        nmsMethod: NmsMethod = NmsMethod.Nms,
    ):
        """Detect objects in given image using rescale strategy."""

        # If image input is diffrent.
        if (self.imwidth != self.netWidth) or (self.imheight != self.netHeight):
            resized = cv2.resize(
                frame,
                (self.netWidth, self.netHeight),
                interpolation=cv2.INTER_LINEAR,
            )
        # If image match network dimensions then use it directly
        else:
            resized = frame

        # Detect objects
        darknet.copy_image_from_bytes(self.image, resized.tobytes())
        boxes, scores, classids = darknet.detect_image(
            self.net,
            self.classes,
            self.image,
            self.imwidth,
            self.imheight,
            thresh=confidence,
            nms=nms_thresh,
            nmsMethod=nmsMethod,
        )
        # Ensemble detections
        boxes, scores, classids = self.EnsembleBoxes(
            boxes,
            scores,
            classids,
            nmsMethod=nmsMethod,
            iou_thresh=nms_thresh,
            conf_thresh=confidence,
        )

        # Convert to detections
        detections = self.ToDetections(boxes, scores, classids)

        return (detections, self.imheight, self.imwidth)

    def detect_letterbox(
        self,
        frame: np.array,
        confidence: float = 0.5,
        nms_thresh: float = 0.45,
        nmsMethod: NmsMethod = NmsMethod.Nms,
    ):
        """Detect objects in given image using strategy."""
        # If frame image has diffrent size than network image.
        if (frame.shape[1] != self.netWidth) or (frame.shape[0] != self.netHeight):
            # Recalculate new width/height of frame with fixed aspect ratio
            newWidth, newHeight = GetFixedFitToBox(
                frame.shape[1], frame.shape[0], self.netWidth, self.netHeight
            )
            # Resize image as newImage with padded zeroes
            newImage = np.zeros([self.netHeight, self.netWidth, 3], dtype=np.uint8)
            newImage[0:newHeight, 0:newWidth] = cv2.resize(
                frame, (newWidth, newHeight), interpolation=cv2.INTER_NEAREST
            )

            # Recalculate frame image dimensions to letter box image
            boundaryWidth = round((self.netWidth * frame.shape[1]) / newWidth)
            boundaryHeight = round((self.netHeight * frame.shape[0]) / newHeight)

        # If (image dimensions == network dimensions) then use it directly.
        else:
            newImage = frame
            newHeight = frame.shape[0]
            newWidth = frame.shape[1]
            boundaryHeight = frame.shape[0]
            boundaryWidth = frame.shape[1]

        # Detect objects
        darknet.copy_image_from_bytes(self.image, newImage.tobytes())
        boxes, scores, classids = darknet.detect_image(
            self.net,
            self.classes,
            self.image,
            boundaryWidth,
            boundaryHeight,
            thresh=confidence,
            nms=nms_thresh,
            nmsMethod=nmsMethod,
        )

        # Ensemble detections
        boxes, scores, classids = self.EnsembleBoxes(
            boxes,
            scores,
            classids,
            nmsMethod=nmsMethod,
            iou_thresh=nms_thresh,
            conf_thresh=confidence,
        )

        # Convert to detections
        detections = self.ToDetections(boxes, scores, classids)

        return detections, self.imheight, self.imwidth

    def detect_tiling_2x2(
        self,
        frame: np.array,
        confidence: float = 0.5,
        nms_thresh: float = 0.45,
        nmsMethod: NmsMethod = NmsMethod.Nms,
    ):
        """Detect objects in given image using rescale strategy."""
        # Frame : Rescale to 2x network dimensions
        scale_x = frame.shape[1] / (2 * self.netWidth)
        scale_y = frame.shape[0] / (2 * self.netHeight)
        rescaled_to_2x2 = cv2.resize(
            frame,
            (2 * self.netWidth, 2 * self.netHeight),
            interpolation=cv2.INTER_LINEAR,
        )

        # Image : Divide into 4 tiles
        tiles = []
        for row in range(2):
            for col in range(2):
                x1 = col * self.netWidth
                x2 = x1 + self.netWidth
                y1 = row * self.netHeight
                y2 = y1 + self.netHeight
                tiles.append(
                    ImageTile(
                        image=rescaled_to_2x2[y1:y2, x1:x2], offset_x=x1, offset_y=y1
                    )
                )

        # Detections : Detect 4 tiles
        tiles_detections = []
        for tile in tiles:
            # Detector : Detect tile image
            darknet.copy_image_from_bytes(self.image, tile.image.tobytes())
            boxes, scores, classids = darknet.detect_image(
                self.net,
                self.classes,
                self.image,
                self.netWidth,
                self.netHeight,
                thresh=confidence,
                nms=nms_thresh,
                nmsMethod=nmsMethod,
            )

            # Ensemble detections
            boxes, scores, classids = self.EnsembleBoxes(
                boxes,
                scores,
                classids,
                nmsMethod=nmsMethod,
                iou_thresh=nms_thresh,
                conf_thresh=confidence,
            )

            # Boxes : Add offset to boxes
            boxes = [
                (
                    x + tile.offset_x,
                    y + tile.offset_y,
                    x2 + tile.offset_x,
                    y2 + tile.offset_y,
                )
                for x, y, x2, y2 in boxes
            ]

            # Boxes : Rescale to original image dimensions
            boxes = [
                (
                    round(x * scale_x),
                    round(y * scale_y),
                    round(x2 * scale_x),
                    round(y2 * scale_y),
                )
                for x, y, x2, y2 in boxes
            ]

            # Convert to detections
            detections = self.ToDetections(boxes, scores, classids)

            tiles_detections.append(detections)

        # Tiles detections : Merge all possible detections.(simple)
        detections = tiles_detections_merge(tiles_detections)

        return (detections, self.imheight, self.imwidth)

    def detect_tiling(
        self,
        frame: np.array,
        confidence: float = 0.5,
        nms_thresh: float = 0.45,
        nmsMethod: NmsMethod = NmsMethod.Nms,
    ):
        """Detect objects in given image using rescale strategy."""
        # Check : Frame shape < 2x network dimensions, fallback to rescale
        if (frame.shape[1] < 2 * self.netWidth) or (
            frame.shape[0] < 2 * self.netHeight
        ):
            return self.detect_rescale(frame, confidence, nms_thresh, nmsMethod)

        # Tiles : Calculate number of tiles
        tiles_cols = ceil(frame.shape[1] / self.netWidth)
        tiles_rows = ceil(frame.shape[0] / self.netHeight)

        # Image : Divide into 4 tiles
        tiles = []
        for row in range(tiles_rows):
            for col in range(tiles_cols):
                x1 = col * self.netWidth
                x2 = x1 + self.netWidth
                y1 = row * self.netHeight
                y2 = y1 + self.netHeight
                tiles.append(
                    ImageTile(image=frame[y1:y2, x1:x2], offset_x=x1, offset_y=y1)
                )

        # Detections : Detect tiles
        tiles_detections = []
        for tile in tiles:
            # Detector : Detect tile image
            darknet.copy_image_from_bytes(self.image, tile.image.tobytes())
            boxes, scores, classids = darknet.detect_image(
                self.net,
                self.classes,
                self.image,
                self.netWidth,
                self.netHeight,
                thresh=confidence,
                nms=nms_thresh,
                nmsMethod=nmsMethod,
            )

            # Ensemble detections
            boxes, scores, classids = self.EnsembleBoxes(
                boxes,
                scores,
                classids,
                nmsMethod=nmsMethod,
                iou_thresh=nms_thresh,
                conf_thresh=confidence,
            )

            # Boxes : Add offset to boxes
            boxes = [
                (
                    x + tile.offset_x,
                    y + tile.offset_y,
                    x2 + tile.offset_x,
                    y2 + tile.offset_y,
                )
                for x, y, x2, y2 in boxes
            ]

            # Convert to detections
            detections = self.ToDetections(boxes, scores, classids)

            tiles_detections.append(detections)

        # Tiles detections : Merge all possible detections.(simple)
        detections = tiles_detections_merge(tiles_detections)

        return (detections, self.imheight, self.imwidth)

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
        # Pre check
        if frame is None:
            logging.error("(Detector) Image invalid!")
            return []

        # Get input frame details
        self.imheight, self.imwidth, channels = frame.shape

        # Create frame object we will use each time, w
        # with dimensions of network width,height.
        if self.image is None:
            self.image = darknet.make_image(self.netWidth, self.netHeight, channels)

        # Detections list
        detections = []

        # Image strategy : Select strategy to use
        if image_strategy == ImageStrategy.Rescale:
            detections, boundaryHeight, boundaryWidth = self.detect_rescale(
                frame, confidence, nms_thresh, nmsMethod
            )
        elif image_strategy == ImageStrategy.LetterBox:
            detections, boundaryHeight, boundaryWidth = self.detect_letterbox(
                frame, confidence, nms_thresh, nmsMethod
            )
        elif image_strategy == ImageStrategy.Tiling2x2:
            detections, boundaryHeight, boundaryWidth = self.detect_tiling_2x2(
                frame, confidence, nms_thresh, nmsMethod
            )
        elif image_strategy == ImageStrategy.Tiling:
            detections, boundaryHeight, boundaryWidth = self.detect_tiling(
                frame, confidence, nms_thresh, nmsMethod
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
