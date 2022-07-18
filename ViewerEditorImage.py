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
    QDrawDistances, CreateRectangle, QPointToTuple, QPointListToTupleList,\
    CvImage2QtImage, CvRGBColorToQColor
from helpers.boxes import PointToRelative, PointToAbsolute
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QBrush, QFont, QPixmap
from PyQt5.Qt import QPoint, QTimer
from PyQt5.QtCore import Qt, pyqtSignal
from Gui.colors import GetNextTableColor, GetTableColor, ColorCycler,\
    colorSchemeMatplotlib, gray
import logging


class ViewerEditorImage(QWidget):
    ''' States of editor.'''
    ModeNone = 0
    ModeEditorAnnotation = 1

    # Define signals
    signalEditorFinished = pyqtSignal(int, name='EditorFinished')
    signalMediaNextSecond = pyqtSignal(datetime, name='MediaNextSecond')

    def __init__(self, parent):
        # QWidget constructor call
        super().__init__(parent=parent)

        # ----- Viewed data ------
        # Background image loaded
        self.imageBg = None
        # Annotations for image
        self.annotations = None
        # Used color cycler
        self.colorCycler = ColorCycler(scheme=colorSchemeMatplotlib)

        # Default data
        # --------------------
        self.colorCycler.Reset()
        self.defaultLanes = [{'name': 'L', 'id': 'L', 'trajectory': [], 'color':CvBGRColorToQColor(self.colorCycler.GetNextColor())},
                             {'name': 'P', 'id': 'P', 'trajectory': [], 'color':CvBGRColorToQColor(
                                 self.colorCycler.GetNextColor())}
                             ]

        # ----- Editor data ------
        # Editor mode
        self.editorMode = self.ModeNone
        # Editor extra argument for mode
        self.editorModeArgument = None
        # Current mouse coords
        self.mouseCoords = None
        # List of all clicks
        self.mouseClicks = []
        # Is dragging
        self.mouseDragging = False

        # UI init and show
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

    def SetEditorMode(self, mode, argument=None):
        ''' Sets editor mode.'''
        self.editorMode = mode
        self.editorModeArgument = argument
        # Set mouse tracking for editing/painting modes
        if (self.editorMode != self.ModeNone):
            self.setMouseTracking(True)

        return True

    def __resetEditorMode(self):
        ''' Resets editor mode.'''
        self.mouseCoords = None
        self.mouseClicks = []
        self.mouseDragging = False
        self.editorMode = self.ModeNone
        self.editorModeArgument = None
        self.setMouseTracking(False)

    def Reset(self):
        ''' Resets all data.'''

    def SetAnnotations(self, annotations):
        ''' Set imagePath to show.'''
        if (annotations is not None):
            self.annotations = annotations
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

    def mouseMoveEvent(self, event):
        ''' Handle mouse move event.'''
        if (self.editorMode != self.ModeNone):
            self.mouseCoords = event.pos()
            self.update()

    def mousePressEvent(self, event):
        ''' Handle mouse event.'''
        if (self.editorMode != self.ModeNone):
            # Left button appends new point
            if (event.buttons() == Qt.LeftButton):
                point = event.pos()
                # Mode ROI
                if (self.editorMode == self.ModeEditorROI):
                    point = self._SnapToBorders(point)
                # Mode
                # Add to clicks
                self.mouseClicks.append(point)
            # Right button finishes drawing
            elif event.buttons() == Qt.RightButton:
                self.__calbackEditorFinished()

        # Editor mode - deleting of area
        if (self.editorMode == self.ModeEditorDeleteArea) and (len(self.mouseClicks) != 0):
            point = self.mouseClicks[-1]
            area = self._GetSnappedArea(point.x(), point.y())
            if (area is not None):
                self.areas.remove(area)
                self.__calbackEditorFinished()

        # Editor mode - deleting of lane
        if (self.editorMode == self.ModeEditorDeleteLane) and (len(self.mouseClicks) != 0):
            point = self.mouseClicks[-1]
            lane = self._GetSnappedLane(point.x(), point.y())
            if (lane is not None):
                self.lanes.remove(lane)
                self.__calbackEditorFinished()

        # Editor mode - deleting of distance
        if (self.editorMode == self.ModeEditorDeleteDistance) and (len(self.mouseClicks) != 0):
            point = self.mouseClicks[-1]
            distance = self._GetSnappedDistance(point.x(), point.y())
            if (distance is not None):
                self.distances.remove(distance)
                self.__calbackEditorFinished()

        # Editor mode - Distance
        if (self.editorMode == self.ModeEditorDistance):
            if (len(self.mouseClicks) == 4):
                self.__calbackEditorFinished()

        # Editor mode - Obstacle
        if (self.editorMode == self.ModeEditorObstacle):
            if (len(self.mouseClicks) == 2):
                self.__calbackEditorFinished()

    def mouseReleaseEvent(self, event):
        ''' Handle mouse event.'''

        # Clear mouse clicks data
        self.mouseClicks = []

    def __calbackEditorFinished(self):
        ''' Finished editor mode.'''
        # Get Preview info width & height
        width, height = self.rect().getRect()[2:]
        # Mouse clicks to relative trajectory
        trajectory = self.AbsoluteQTrajectoryToTrajectory(
            self.mouseClicks, width, height)

        previousMode = self.editorMode
        self.__resetEditorMode()
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
            # Get geometry of widget
            area = self.geometry()
            # Fill black background
            widgetPainter.fillRect(area, QBrush(Qt.black))
            widgetPainter.setPen(Qt.white)
            widgetPainter.setFont(QFont('Decorative', 10))
            widgetPainter.drawText(area, Qt.AlignCenter,
                                   'No image loaded!')

        # Draw all annotations
        for annotate in self.annotations:
            annotate.QtDraw(widgetPainter, isConfidence=True)

        widgetPainter.end()
