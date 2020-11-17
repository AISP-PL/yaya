'''
Created on 22 sie 2020

@author: spasz
'''
from ObjectDetectors.yolov4 import darknet
from helpers.boxes import ToRelative


class DetectorYOLOv4():
    '''
    classdocs
    '''

    def __init__(self, cfgPath, weightPath, metaPath):
        '''
        Constructor
        '''
        self.net, self.classes, self.colors = darknet.load_network(
            cfgPath, metaPath, weightPath)
        self.image = None

    def Detect(self, image, confidence=0.5, nms_thresh=0.45, boxRelative=False):
        ''' Detect objects in given image'''
        # Create image object we will use each time
        if (self.image is None):
            imheight, imwidth, channels = image.shape
            # Create an image we reuse for each detect
            self.image = darknet.make_image(imwidth, imheight, channels)

        # Detect objects
        darknet.copy_image_from_bytes(self.image, image.tobytes())
        detections = darknet.detect_image(
            self.net, self.classes, self.image, thresh=confidence, nms=nms_thresh)

        # Change box coordinates to rectangle
        h, w = image.shape[0:2]
        for i, d in enumerate(detections):
            className, confidence, box = d
            if (boxRelative is True):
                box = ToRelative(darknet.bbox2points(box), w, h)
            else:
                box = darknet.bbox2points(box)
            detections[i] = (className, confidence, box)

        return detections

    def Draw(self, image, bboxes, labels, confidences):
        ''' Draw all boxes on image'''
        return darknet.draw_boxes(image, bboxes, labels, confidences, self.colors)

    def GetClassNames(self):
        ''' Returns all class names.'''
        return self.classes

    def GetAllowedClassNames(self):
        ''' Returns all interesing us class names.'''
        return self.classes
