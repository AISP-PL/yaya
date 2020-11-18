'''
Created on 16 lis 2020

@author: spasz
'''

from engine.annote import GetClasses
from helpers.images import ResizeToWidth
import cv2
import helpers.boxes as boxes


class Gui(object):
    def __init__(self, name):
        self.image = None
        self.winname = name
        self.annoter = None
        self.coords = []
        self.dragging = False

    def SetAnnoter(self, annoter):
        ''' Set annoter .'''
        self.annoter = annoter

    def Start(self):
        ''' Start gui running.'''
        # GUI keyboard loop
        key = 0
        self.annoter.Process()
        while (key != 27):
            key = 0

            # Resize image
            self.image = self.annoter.GetImage()
            self.image = ResizeToWidth(self.image)

            # Create CV2 window
            cv2.namedWindow(self.winname)
            # Images slider
            cv2.createTrackbar('Images', self.winname,
                               0, self.annoter.GetImagesCount()-1, self._images_trackbar_cb)
            # Classes slider
            cv2.createTrackbar('Classes', self.winname, 0,
                               len(GetClasses())-1, self._classes_trackbar_cb)
            # Mouse handling
            cv2.setMouseCallback(self.winname, self._mouse_cb)

            # Update window
            self._update()

            # Loop waiting for specific keys
            keyAction = False
            while (keyAction == False):
                key = cv2.waitKeyEx()
                keyAction = self._keyboard_cb(key)

        cv2.destroyWindow(self.winname)
        return self.coords if self.coords else None

    def _classes_trackbar_cb(self, arg):
        ''' Callback from trackbar.'''
        # do nothing

    def _images_trackbar_cb(self, arg):
        ''' Callback from trackbar.'''
        imageNumber = cv2.getTrackbarPos('Images', self.winname)
        self.annoter.SetImageNumber(imageNumber)
        self.image = self.annoter.GetImage()
        self.image = ResizeToWidth(self.image)
        self._update()

    def _keyboard_cb(self, key):
        '''
            Keyboard callback.
            - Return True - exit from keyboard loop.
        '''
        # Application exit
        if (key == 27):
            return True
        # TODO keys 0-9
        # TODO key save 'Ctrl+s'
        # TODO key clear 'c'
        # TODO key remove 'r'
        elif (key >= ord('0')) and (key <= ord('9')):
            classNumber = key - ord('0')
            cv2.setTrackbarPos('Classes', self.winname, classNumber)
        # Next image
        elif (key == 65363) or (key == ord('.')):
            self.annoter.ProcessNext()
            return True
        # Prev image
        elif (key == 65361) or (key == ord(',')):
            self.annoter.ProcessPrev()
            return True

        return False

    def _mouse_cb(self, event, x, y, flags, parameters):
        # Record starting (x,y) coordinates on left mouse button click
        if event == cv2.EVENT_LBUTTONDOWN:
            self.coords[:] = [(x, y)]
            self.dragging = True

        elif event == 0 and self.dragging:
            self.coords[1:] = [(x, y)]

        # Record ending (x,y) coordintes on left mouse bottom release
        elif event == cv2.EVENT_LBUTTONUP:
            self.dragging = False
            self.coords[1:] = [(x, y)]
            xs, ys = list(zip(*self.coords))
            self.coords = (min(xs), min(ys),
                           max(xs), max(ys))
            height, width = self.image.shape[0:2]
            box = boxes.ToRelative(self.coords, width, height)
            classNumber = cv2.getTrackbarPos('Classes', self.winname)
            self.annoter.AddAnnotation(box, classNumber)
            self.coords = []

        # Clear drawing boxes on right mouse button click
        elif event == cv2.EVENT_RBUTTONDOWN:
            self.coords = []
            self.dragging = False

        self._update()

    def _update(self):
        ''' Update image view.'''
        im = self.image.copy()

        # Draw currrent rectangle
        if len(self.coords) == 2:
            cv2.rectangle(im, self.coords[0], self.coords[1], (0, 255, 0), 1)

        # Draw all annotations
        annotations = self.annoter.GetAnnotations()
        if (annotations is not None) and (len(annotations)):
            for annotate in annotations:
                annotate.Draw(im)

        cv2.setTrackbarPos('Images', self.winname,
                           self.annoter.GetImageNumber())
        cv2.imshow(self.winname, im)
