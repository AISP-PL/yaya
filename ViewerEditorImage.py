'''
Created on 30 gru 2020

@author: spasz
'''
import os
import subprocess
import cv2
from datetime import datetime
from helpers.QtDrawing import QDrawPolygon, QDrawPolyline, QDrawJoints,\
    QDrawCrosshair, QDrawText, QDrawArrow, CvBGRColorToQColor, QDrawRectangle,\
    CvImage2QtImage, CvRGBColorToQColor
from helpers.boxes import PointToRelative, PointToAbsolute, PointsToRect
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QBrush, QFont
from PyQt5.Qt import QPoint, QTimer
from PyQt5.QtCore import Qt, pyqtSignal
import helpers.boxes as boxes
import logging


class ViewerEditorImage(QWidget):
    ''' States of editor.'''
    ModeNone = 0
    ModeAddAnnotation = 1
    ModeRemoveAnnotation = 2
    ModePaintCircle = 3

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
        }
        # Background image loaded
        self.imageBg = None
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
        self.mouseClicks = []
        self.mouseDragging = False
        self.editorMode = defaultMode
        self.editorModeArgument = None

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

    def mouseMoveEvent(self, event):
        ''' Handle mouse move event.'''
        self.mousePosition = event.pos()
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
                    self.mouseClicks = [event.pos()]
                    self.CallbackEditorFinished()

            # RPM returns
            elif (event.buttons() == Qt.RightButton):
                self.CallbackEditorFinished()

        # Mode Paint circle
        elif (self.editorMode == self.ModePaintCircle):
            # LPM finds annotation
            if (event.buttons() == Qt.LeftButton):
                viewWidth, viewHeight = self.GetViewSize()
                imWidth, imHeight = self.GetImageSize()
                viewPoint = event.pos().x(), event.pos().y()
                relPoint = PointToRelative(viewPoint, viewWidth, viewHeight)
                imPoint = PointToAbsolute(relPoint, imWidth, imHeight)

                # Add drawing to original image
                self.annoter.PaintCircles([imPoint],
                                          self.editorModeArgument,
                                          (0, 0, 0))

    def mouseReleaseEvent(self, event):
        ''' Handle mouse event.'''

    def CallbackEditorFinished(self):
        ''' Finished editor mode.'''
        # Get Preview info width & height
        width, height = self.GetViewSize()
        # Mouse clicks to relative trajectory
        trajectory = self.AbsoluteQTrajectoryToTrajectory(
            self.mouseClicks, width, height)

        # Mode Add Annotation
        if (self.editorMode == self.ModeAddAnnotation):
            box = PointsToRect(trajectory[0], trajectory[1])
            self.annoter.AddAnnotation(box,
                                       self.classNumber)
        # Mode Remove Annotation
        elif (self.editorMode == self.ModeRemoveAnnotation):
            toDelete = self.GetHoveredAnnotation(trajectory[0])
            # If clicked on annotation the return
            if (toDelete is not None):
                self.annoter.RemoveAnnotation(toDelete)

        previousMode = self.editorMode
        self.__resetEditorMode(previousMode)
        self.update()

        # Emit signal
        self.signalEditorFinished.emit(previousMode)

    def paintEvent(self, event):
        ''' Draw on every paint event.'''
        # Get Preview info width & height
        viewWidth, viewHeight = self.GetViewSize()

        # Create painter
        widgetPainter = QPainter()
        widgetPainter.begin(self)

        # If image is loaded?
        if (self.imageBg is not None):
            image = self.imageBg
            pixmap = CvImage2QtImage(image)
            widgetPainter.drawPixmap(self.rect(), pixmap)
        # If there is no image then fill Black and draw text
        else:
            # Fill black background
            widgetPainter.fillRect(self.geometry(),
                                   QBrush(Qt.black))
            widgetPainter.setPen(Qt.white)
            widgetPainter.setFont(QFont('Decorative', 10))
            widgetPainter.drawText(self.geometry(),
                                   Qt.AlignCenter,
                                   'No image loaded!')

        # Draw all annotations
        if (not self.config['isAnnotationsHidden']):
            for annotate in self.annoter.GetAnnotations():
                annotate.QtDraw(widgetPainter,
                                isConfidence=True)

            # Draw hovered annotation
            if (self.mousePosition is not None):
                # Get hovered annotation
                annote = self.GetHoveredAnnotation(
                    boxes.PointToRelative((self.mousePosition.x(), self.mousePosition.y()),
                                          viewWidth, viewHeight))
                if (annote is not None):
                    annote.QtDraw(widgetPainter,
                                  highlight=True,
                                  isConfidence=True)

        # -------- Mode Annotation Draw -------
        if (self.editorMode == self.ModeAddAnnotation):
            if (len(self.mouseClicks) != 0) and (self.mousePosition is not None):
                # Draw rectangle box
                QDrawRectangle(widgetPainter,
                               [self.mouseClicks[0], self.mousePosition],
                               pen=Qt.green,
                               brushColor=Qt.green,
                               brushOpacity=0.1
                               )

        # Draw crosshair
        if (self.mousePosition is not None):
            QDrawCrosshair(widgetPainter, self.mousePosition.x(), self.mousePosition.y(),
                           viewWidth, viewHeight, Qt.red)

        widgetPainter.end()
