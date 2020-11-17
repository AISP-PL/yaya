'''
Created on 16 lis 2020

@author: spasz
'''
from engine.annote import GetClasses
from helpers.images import ResizeToWidth
import cv2


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
        # Resize image
        self.annoter.ProcessNext()
        self.image = self.annoter.GetImage()
        self.image = ResizeToWidth(self.image)

        # Create CV2 window
        cv2.namedWindow(self.winname)
        # Images slider
        cv2.createTrackbar('Images', self.winname, 0, 255, self._trackbar_cb)
        # Classes slider
        cv2.createTrackbar('Classes', self.winname, 0,
                           len(GetClasses())-1, self._trackbar_cb)
        # Mouse handling
        cv2.setMouseCallback(self.winname, self._mouse_cb)

        # Update window
        self._update()

        # GUI keyboard loop
        key = 0
        while (key != 27):
            key = cv2.waitKey()
            self._keyboard_cb(key)

        cv2.destroyWindow(self.winname)
        return self.coords if self.coords else None

    def _trackbar_cb(self):
        ''' Callback from trackbar.'''

    def _keyboard_cb(self, key):
        ''' Keyboard callback.'''

    def _mouse_cb(self, event, x, y, flags, parameters):
        # Record starting (x,y) coordinates on left mouse button click
        if event == cv2.EVENT_LBUTTONDOWN:
            self.coords[:] = [(x, y)]
            self.dragging = True

        elif event == 0 and self.dragging:
            self.coords[1:] = [(x, y)]

        # Record ending (x,y) coordintes on left mouse bottom release
        elif event == cv2.EVENT_LBUTTONUP:
            self.coords[1:] = [(x, y)]
            self.dragging = False
            xs, ys = list(zip(*self.coords))
            self.coords = [(min(xs), min(ys)),
                           (max(xs), max(ys))]
            print('roi:', self.coords)

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

        cv2.imshow(self.winname, im)
