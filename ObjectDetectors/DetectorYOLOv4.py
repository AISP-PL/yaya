'''
Created on 22 sie 2020

@author: spasz
'''
import os
import logging
import cv2
import numpy as np
from ObjectDetectors.yolov4 import darknet
from ObjectDetectors.common.Detector import Detector, NmsMethod
from helpers.files import GetFilepath
from math import ceil
from helpers.images import GetFixedFitToBox
from helpers.boxes import ToRelative


class DetectorYOLOv4(Detector):
    '''
    classdocs
    '''
    # Image fitting strategies
    StrategyRescale = 0
    StrategyLetterBox = 1

    def __init__(self,
                 cfgPath,
                 weightPath,
                 dataPath,
                 name='YOLOv4',
                 imageStrategy=None,
                 ):
        '''
        Constructor
        '''
        Detector.__init__(self, id=0, gpuid=0, name=name)
        # Store yolo configuartion paths
        self.config = {'Config': cfgPath,
                       'Weights': weightPath,
                       'Names': dataPath,
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
        if (self.imageStrategy is None):
            self.imageStrategy = int(os.environ.get(
                'DETECTORYOLOV4_STRATEGY', '0'))
        # List of colors matched with labels
        self.colors = []
        # Pre-Read and strip all labels
        self.classes = open(GetFilepath(
            dataPath, dropExtension=True)+'.names').read().splitlines()
        self.classes = list(map(str.strip, self.classes))  # strip names

        # Validate labels
        self.__validateLabels()

    def __del__(self):
        ''' Destructor.'''
        # Free network image
        if (self.image is not None):
            darknet.free_image(self.image)

        # Unload network from memory
        if (self.net is not None):
            darknet.free_network_ptr(self.net)

    def __validateLabels(self):
        ''' Validated loaded labels.'''
        # Check if last label is empty (could be because of \n)
        if (self.classes[-1] == '') or (len(self.classes[-1]) == 0):
            del self.classes[-1]
            logging.warning('(DetectorYOLOv4) Removed last empty label!')
        # Check labels integrity
        for c in self.classes:
            # Check for missing labels
            if (len(c) == 0):
                logging.fatal(
                    '(DetectorYOLOv4) Missing label \'%s\' for class!', c)
                raise ValueError()

    def IsInitialized(self):
        ''' Return True if detector is initialized.'''
        return (self.net is not None)

    def Init(self):
        ''' Init call with other arguments.'''
        # Choose GPU to use for YOLO
        darknet.set_gpu(self.gpuid)
        # YOLO net, labels, cfg
        self.net, self.classes, self.colors = darknet.load_network(
            self.config['Config'],
            self.config['Names'],
            self.config['Weights'])

        # Get network  input (width and height)
        self.netWidth = darknet.network_width(self.net)
        self.netHeight = darknet.network_height(self.net)

        # Validate detector
        self.__validateLabels()

        logging.info('(DetectorYOLOv4) Created %ux%u network with %u classes.',
                     self.netWidth,
                     self.netHeight,
                     len(self.classes),
                     )

    def GetWidth(self):
        ''' Returns network image width.'''
        return self.netWidth

    def GetHeight(self):
        ''' Returns network image height.'''
        return self.netHeight

    def Detect(self, 
               frame, 
               confidence=0.5, 
               nms_thresh=0.45, 
               boxRelative=False,
               nmsMethod:NmsMethod=NmsMethod.Nms,
               ):
        ''' Detect objects in given frame'''
        # Pre check
        if (frame is None):
            logging.error('(Detector) Image invalid!')
            return []

        # Get input frame details
        self.imheight, self.imwidth, channels = frame.shape

        # Create frame object we will use each time, w
        # with dimensions of network width,height.
        if (self.image is None):
            self.image = darknet.make_image(self.netWidth,
                                            self.netHeight,
                                            channels)

        # Detections list
        detections = []
        # ------------ Strategies choose
        # 1. Strategy rescale.
        # Rescale input image to network image dimensions.
        if (self.imageStrategy == self.StrategyRescale):
            # If image input is diffrent.
            if (self.imwidth != self.netWidth) or (self.imheight != self.netHeight):
                resized = cv2.resize(frame,
                                     (self.netWidth, self.netHeight),
                                     interpolation=cv2.INTER_LINEAR)
            # If image match network dimensions then use it directly
            else:
                resized = frame

            # Detect objects
            darknet.copy_image_from_bytes(self.image, resized.tobytes())
            detections = darknet.detect_image(self.net,
                                              self.classes,
                                              self.image,
                                              self.imwidth,
                                              self.imheight,
                                              thresh=confidence,
                                              nms=nms_thresh,
                                              nmsMethod=nmsMethod)

            # Change box coordinates to rectangle
            if (boxRelative is True):
                h, w = self.imheight, self.imwidth
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
                    detections[i] = (className, confidence,
                                     ToRelative(box, w, h))

        # 2. Strategy letter box.
        # Rescale input image to network image dimensions.
        elif (self.imageStrategy == self.StrategyLetterBox):
            # If frame image has diffrent size than network image.
            if (frame.shape[1] != self.netWidth) or (frame.shape[0] != self.netHeight):
                # Recalculate new width/height of frame with fixed aspect ratio
                newWidth, newHeight = GetFixedFitToBox(frame.shape[1], frame.shape[0],
                                                       self.netWidth, self.netHeight)
                # Resize image as newImage with padded zeroes
                newImage = np.zeros(
                    [self.netHeight, self.netWidth, 3], dtype=np.uint8)
                newImage[0:newHeight, 0:newWidth] = cv2.resize(frame, (newWidth, newHeight),
                                                               interpolation=cv2.INTER_NEAREST)

                # Recalculate frame image dimensions to letter box image
                boundaryWidth = round(
                    (self.netWidth * frame.shape[1])/newWidth)
                boundaryHeight = round(
                    (self.netHeight * frame.shape[0])/newHeight)

            # If (image dimensions == network dimensions) then use it directly.
            else:
                newImage = frame
                newHeight = frame.shape[0]
                newWidth = frame.shape[1]
                boundaryHeight = frame.shape[0]
                boundaryWidth = frame.shape[1]

            # Detect objects
            darknet.copy_image_from_bytes(self.image, newImage.tobytes())
            detections = darknet.detect_image(self.net,
                                              self.classes,
                                              self.image,
                                              boundaryWidth,
                                              boundaryHeight,
                                              thresh=confidence,
                                              nms=nms_thresh,
                                              nmsMethod=nmsMethod)

            # Change box coordinates to rectangle
            if (boxRelative is True):
                h, w = boundaryWidth, boundaryWidth
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
                    detections[i] = (className, confidence,
                                     ToRelative(box, w, h))

        return detections
