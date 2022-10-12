'''
Created on 30 gru 2020

@author: spasz
'''
import os
import subprocess
import cv2
import numpy as np
from datetime import datetime
from helpers.QtDrawing import QDrawPolygon, QDrawPolyline, QDrawJoints,\
    QDrawCrosshair, QDrawText, QDrawArrow, CvBGRColorToQColor, QDrawRectangle,\
    CvImage2QtImage, CvRGBColorToQColor, QDrawElipse
from helpers.boxes import PointToRelative, PointToAbsolute, PointsToRect
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QBrush, QFont, QPixmap
from PyQt5.Qt import QPoint, QTimer
from PyQt5.QtCore import Qt, pyqtSignal
import helpers.boxes as boxes
import logging
from helpers.images import GetFixedFitToBox
from engine.annote import AnnoteAuthorType


class ViewerEditorImage(QWidget):
    ''' States of editor.'''
    # Editor mode
    ModeNone = 0
    ModeAddAnnotation = 1
    ModeRenameAnnotation = 2
    ModeRemoveAnnotation = 3
    ModePaintCircle = 4

    # Image scaling mode
    ImageScalingResize = 0
    ImageScalingResizeAspectRatio = 1
    ImageScalingOriginalSize = 2

    # Define signals
    signalEditorFinished = pyqtSignal(int, name='EditorFinished')

    def __init__(self, parent):
        # QWidget constructor call
        super().__init__(parent=parent)

        # ----- Viewed data ------
        # Configuration
        self.config = {
            'isConfidence': True,
            'isAnnotationsHidden': False,
            'isLabelsHidden': False,
        }
        # Background image loaded
        self.imageBg = None
        # Mode of scaling image
        self.imageScaling = self.ImageScalingResize
        # Annoter for image
        self.annoter = None
        # Current class number
        self.classNumber = 0

        # ----- Editor data ------
        # Editor mode
        self.editorMode = self.ModeNone
        # Editor extra argument for mode
        self.editorModeArgument = None
        # Current mouse coords
        self.mousePosition = None
        # Mouse trajectory
        self.mouseTrajectory = None
        # List of all clicks
        self.mouseClicks = []
        # Is dragging
        self.mouseDragging = False

        # UI init and show
        self.setMouseTracking(True)
        self.show()

    def TrajectoryToAbsoluteQTrajectory(self, trajectory, width, height):
        '''Recalculate trajectory to Q absolute trajectory.'''
        qtrajectory = []
        for element in trajectory:
            x, y = PointToAbsolute((element[0], element[1]),
                                   width, height)
            qtrajectory.append(QPoint(x, y))

        return qtrajectory

    def AbsoluteQTrajectoryToTrajectory(self, qtrajectory, width, height):
        '''Recalculate trajectory to Q absolute trajectory.'''
        trajectory = []
        for qpoint in qtrajectory:
            x, y = qpoint.x(), qpoint.y()
            x, y = PointToRelative((x, y),
                                   width, height)
            trajectory.append((x, y))

        return trajectory

    def ItemQTrajectoryUpdate(self, item, width, height):
        ''' Update absolute Q trajectory in item.'''
        item['QViewTrajectory'] = self.TrajectoryToAbsoluteQTrajectory(
            item['trajectory'], width, height)
        item['QViewWidth'] = width
        item['QViewHeight'] = height
        return item

    def GetOption(self, name):
        ''' Set configuration option.'''
        if (name in self.config):
            return self.config[name]

        return None

    def SetOption(self, name, value):
        ''' Set configuration option.'''
        if (name in self.config):
            self.config[name] = value
            self.update()
        else:
            logging.error('(ViewerEditorImage) Unknown configuration option!')

    def SetClassNumber(self, index):
        ''' Set class number. '''
        self.classNumber = index

    def SetEditorMode(self, mode, argument=None):
        ''' Sets editor mode.'''
        self.__resetEditorMode()
        self.editorMode = mode
        self.editorModeArgument = argument
        return True

    def SetEditorModeArgument(self, argument):
        ''' Set/update editor mode argument.'''
        self.editorModeArgument = argument

    def __resetEditorMode(self, defaultMode=ModeNone):
        ''' Resets editor mode.'''
        self.mousePosition = None
        self.mouseTrajectory = None
        self.mouseClicks = []
        self.mouseDragging = False
        self.editorMode = defaultMode

    def SetAnnoter(self, annoter):
        ''' Set annoter handle.'''
        if (annoter is not None):
            self.annoter = annoter
            self.update()

    def SetImage(self, image):
        ''' Set imagePath to show.'''
        if (image is not None):
            self.imageBg = image
            self.update()

    def SetImageScaling(self, scalingMode):
        ''' Sets image scaling mode.'''
        self.imageScaling = scalingMode

    def GetImageSize(self):
        ''' Returns .'''
        if (self.imageBg is not None):
            height, width = self.imageBg.shape[0:2]
            return width, height

        return 0, 0

    def GetViewSize(self):
        ''' Returns .'''
        width, height = self.rect().getRect()[2:]
        return width, height

    def GetHoveredAnnotation(self, point):
        ''' Finds currently hovered annotation.'''
        founded = None
        for element in self.annoter.GetAnnotations():
            if (element.IsInside(point) == True):
                if (founded is not None):
                    area1 = boxes.GetArea(element.GetBox())
                    area2 = boxes.GetArea(founded.GetBox())
                    if (area1 < area2):
                        founded = element
                else:
                    founded = element

        return founded

    def SaveScreenshot(self, filepath):
        ''' Returns screenshot.'''
        pixmap = QPixmap((self.size()))
        self.render(pixmap)
        pixmap.save(filepath)

    def ScreenshotToFile(self, path) -> bool:
        '''Public method which renders widget to file.'''
        # Render to pixmap of same width and height
        pixmap = self.grab(self.rect())
        # Save to filepath (return bool)
        return pixmap.save(path)

    def mouseMoveEvent(self, event):
        ''' Handle mouse move event.'''
        self.mousePosition = event.pos()
        if (self.mouseTrajectory is not None):
            self.mouseTrajectory.append(event.pos())

        self.update()

    def mousePressEvent(self, event):
        ''' Handle mouse event.'''
        # Mode Add Annotation
        if (self.editorMode == self.ModeAddAnnotation):
            # LPM adds point
            if (event.buttons() == Qt.LeftButton):
                self.mouseClicks.append(event.pos())
                # If stored 2 points the call finish.
                if (len(self.mouseClicks) >= 2):
                    self.CallbackEditorFinished()

        # Mode Rename Annotation
        elif (self.editorMode == self.ModeRenameAnnotation):
            # LPM finds annotation
            if (event.buttons() == Qt.LeftButton):
                x, y = event.pos().x(), event.pos().y()
                viewWidth, viewHeight = self.GetViewSize()
                toDelete = self.GetHoveredAnnotation(boxes.PointToRelative((x, y),
                                                                           viewWidth, viewHeight))
                # If clicked on annotation the return
                if (toDelete is not None):
                    self.editorModeArgument = toDelete
                    self.CallbackEditorFinished()

        # Mode Remove Annotation
        elif (self.editorMode == self.ModeRemoveAnnotation):
            # LPM finds annotation
            if (event.buttons() == Qt.LeftButton):
                x, y = event.pos().x(), event.pos().y()
                viewWidth, viewHeight = self.GetViewSize()
                toDelete = self.GetHoveredAnnotation(boxes.PointToRelative((x, y),
                                                                           viewWidth, viewHeight))
                # If clicked on annotation the return
                if (toDelete is not None):
                    self.editorModeArgument = toDelete
                    self.CallbackEditorFinished()

        # Mode Paint circle
        elif (self.editorMode == self.ModePaintCircle):
            # LPM finds annotation
            if (event.buttons() == Qt.LeftButton):
                # Enabled mouse trajectory storing
                self.mouseTrajectory = [event.pos()]

    def mouseReleaseEvent(self, event):
        ''' Handle mouse event.'''
        # Mode Paint circle
        if (self.editorMode == self.ModePaintCircle):
            self.CallbackEditorFinished()

    def CallbackEditorFinished(self):
        ''' Finished editor mode.'''
        # Get Preview info width & height
        widgetWidth, widgetHeight = self.GetViewSize()
        # Get image width & height
        imWidth, imHeight = self.GetImageSize()
        # ---------- Select scaling mode -----------
        # Resize
        if (self.imageScaling == self.ImageScalingResize):
            viewportWidth, viewportHeight = widgetWidth, widgetHeight

        # Resize with aspect ratio
        elif (self.imageScaling == self.ImageScalingResizeAspectRatio):
            viewportWidth, viewportHeight = GetFixedFitToBox(
                imWidth, imHeight, widgetWidth, widgetHeight)

        # Original size
        elif (self.imageScaling == self.ImageScalingOriginalSize):
            viewportWidth, viewportHeight = imWidth, imHeight

        # Mouse clicks to relative
        clicksRel = self.AbsoluteQTrajectoryToTrajectory(
            self.mouseClicks, viewportWidth, viewportHeight)
        # Mouse trajectory relative
        if (self.mouseTrajectory is not None):
            trajectoryRel = self.AbsoluteQTrajectoryToTrajectory(
                self.mouseTrajectory, viewportWidth, viewportHeight)

        # Mode Add Annotation
        if (self.editorMode == self.ModeAddAnnotation):
            box = PointsToRect(clicksRel[0], clicksRel[1])
            self.annoter.AddAnnotation(box,
                                       self.classNumber)
        # Mode Rename Annotation
        elif (self.editorMode == self.ModeRenameAnnotation):
            annote = self.editorModeArgument
            annote.SetClassNumber(self.classNumber)
            annote.SetAuthorType(AnnoteAuthorType.byHand)

        # Mode Remove Annotation
        elif (self.editorMode == self.ModeRemoveAnnotation):
            self.annoter.RemoveAnnotation(self.editorModeArgument)

        # Mode Paint circle
        elif (self.editorMode == self.ModePaintCircle):
            imWidth, imHeight = self.GetImageSize()
            for relPoint in trajectoryRel:
                imPoint = PointToAbsolute(relPoint, imWidth, imHeight)
                # Add drawing to original image
                self.annoter.PaintCircles([imPoint],
                                          self.editorModeArgument,
                                          (0, 0, 0))

        previousMode = self.editorMode
        self.__resetEditorMode(previousMode)
        self.update()

        # Emit signal
        self.signalEditorFinished.emit(previousMode)

    def paintEvent(self, event):
        ''' Draw on every paint event.'''
        # Get Preview info width & height
        widgetWidth, widgetHeight = self.GetViewSize()
        # Create painter
        widgetPainter = QPainter()
        widgetPainter.begin(self)

        # If image is loaded?
        if (self.imageBg is not None):
            # Setup image width & height
            imHeight, imWidth = self.imageBg.shape[0:2]
            image = self.imageBg
        # If there is no image then fill Black and draw text
        else:
            # Setup image width & height
            imWidth, imHeight = self.GetViewSize()
            image = np.zeros([imWidth, imHeight, 3], dtype=np.uint8)

        # ---------- Select scaling mode -----------
        # Resize
        if (self.imageScaling == self.ImageScalingResize):
            viewportWidth, viewportHeight = widgetWidth, widgetHeight

        # Resize with aspect ratio
        elif (self.imageScaling == self.ImageScalingResizeAspectRatio):
            viewportWidth, viewportHeight = GetFixedFitToBox(
                imWidth, imHeight, widgetWidth, widgetHeight)
            widgetPainter.setViewport(0, 0, viewportWidth, viewportHeight)

        # Original size
        elif (self.imageScaling == self.ImageScalingOriginalSize):
            widgetPainter.setViewport(0, 0, imWidth, imHeight)
            viewportWidth, viewportHeight = imWidth, imHeight

        # Recalculate mouse position to viewport
        mousePosition = None
        if (self.mousePosition is not None):
            mx, my = boxes.PointToRelative((self.mousePosition.x(), self.mousePosition.y()),
                                           viewportWidth, viewportHeight)
            mousePosition = QPoint(mx*widgetWidth, my*widgetHeight)

        # Recalculate mouse clicks to viewport
        mouseClicks = []
        if (len(self.mouseClicks)):
            for mouseClick in self.mouseClicks:
                mx, my = boxes.PointToRelative((mouseClick.x(), mouseClick.y()),
                                               viewportWidth, viewportHeight)
                mouseClicks.append(QPoint(mx*widgetWidth, my*widgetHeight))

        # Draw current OpenCV image as pixmap
        pixmap = CvImage2QtImage(image)
        widgetPainter.drawPixmap(self.rect(), pixmap)

        # Draw all annotations
        if (not self.config['isAnnotationsHidden']):
            for annotate in self.annoter.GetAnnotations():
                annotate.QtDraw(widgetPainter,
                                isConfidence=True,
                                isLabel=not self.config['isLabelsHidden'])

            # Draw hovered annotation
            if (mousePosition is not None):
                # Get hovered annotation
                annote = self.GetHoveredAnnotation(
                    boxes.PointToRelative((self.mousePosition.x(), self.mousePosition.y()),
                                          viewportWidth, viewportHeight))
                if (annote is not None):
                    annote.QtDraw(widgetPainter,
                                  highlight=True,
                                  isConfidence=True,
                                  isLabel=True)

        # -------- Mode Annotation Draw -------
        if (self.editorMode == self.ModeAddAnnotation):
            if (len(mouseClicks) != 0) and (mousePosition is not None):
                # Draw rectangle box
                QDrawRectangle(widgetPainter,
                               [mouseClicks[0], mousePosition],
                               pen=Qt.green,
                               brushColor=Qt.green,
                               brushOpacity=0.1
                               )

        # -------- Mode Paint Draw -------
        if (self.editorMode == self.ModePaintCircle):
            if (mousePosition is not None):
                imWidth, imHeight = self.GetImageSize()
                radius = round((self.editorModeArgument/imWidth)*viewportWidth)
                QDrawElipse(widgetPainter,
                            mousePosition,
                            radius)

        # Draw crosshair
        if (mousePosition is not None):
            QDrawCrosshair(widgetPainter, mousePosition.x(), mousePosition.y(),
                           widgetWidth, widgetHeight, Qt.red)

        widgetPainter.end()
