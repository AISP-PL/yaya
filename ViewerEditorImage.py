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
    ModeEditorArea = 1
    ModeEditorDeleteArea = 2
    ModeEditorLane = 3
    ModeEditorDeleteLane = 4
    ModeEditorROI = 5
    ModeEditorDistance = 6
    ModeEditorDeleteDistance = 7
    ModeEditorFraming = 8
    ModeEditorObstacle = 9

    # Define signals
    signalEditorFinished = pyqtSignal(int, name='EditorFinished')
    signalMediaNextSecond = pyqtSignal(datetime, name='MediaNextSecond')

    def __init__(self, parent):
        # QWidget constructor call
        super().__init__(parent=parent)

        # ----- Viewed data ------
        # Location path
        self.location = None
        # Image Pixmap being processed
        self.imagePath = None
        # Background image loaded
        self.imageBg = None
        # Used color cycler
        self.colorCycler = ColorCycler(scheme=colorSchemeMatplotlib)

        # ----- Created data -----
        self.areas = []

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
        # Radius of snap to lane
        self.snapToLaneRadius = 20
        # Radius of snap to border
        self.snapToBorderRadius = 40

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
        # Do extra argument checks for mode = Framing
        if (mode == self.ModeEditorFraming):
            # Check minimal image shape
            width, height = argument
            imheight, imwidth = self.imageBg.shape[0:2]
            viewwidth, viewheight = self.GetViewSize()
            self.framing.SetViewSize(viewwidth, viewheight)
            self.framing.SetImageSize(imwidth, imheight)
            if (self.framing.SetProportions(width, height) is False):
                logging.error('Image smaller than framing!')
                return False

        # Check ok, mode could be set.
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

    def SetImage(self, path):
        ''' Set imagePath to show.'''
        self.imagePath = path
        self.update()

    def GetFraming(self):
        ''' Returns framing.'''
        return self.framing

    def GetViewSize(self):
        ''' Returns .'''
        width, height = self.rect().getRect()[2:]
        return width, height

    def GetImageSize(self):
        ''' Returns .'''
        if (self.imageBg is not None):
            height, width = self.imageBg.shape[0:2]
            return width, height

        return 0, 0

    def OpenLocation(self, location, presenter):
        ''' Sets configuration.'''
        # Set location handle
        self.location = location

        # Update UI
        self.update()

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
        # Framing mode
        if (self.editorMode == self.ModeEditorFraming):
            point = self.mouseClicks[0]
            releasepoint = event.pos()
            dx = releasepoint.x() - point.x()
            dy = releasepoint.y() - point.y()

            # Moving mode
            if (self._GetSnappedPoint(point.x(), point.y(),
                                      [self.framing.GetBottomLeftToView()]) is not None):
                self.framing.Move(dx, dy)

            # Resize mode
            if (self._GetSnappedPoint(point.x(), point.y(),
                                      [self.framing.GetTopRightToView()]) is not None):
                self.framing.Resize(dx, dy)

            # Clear mouse clicks data
            self.mouseClicks = []

    def __calbackEditorFinished(self):
        ''' Finished editor mode.'''
        # Get Preview info width & height
        width, height = self.rect().getRect()[2:]
        # Mouse clicks to relative trajectory
        trajectory = self.AbsoluteQTrajectoryToTrajectory(
            self.mouseClicks, width, height)

        # Area editor mode
        if (self.editorMode == self.ModeEditorArea):
            self.__addArea(areatype=self.editorModeArgument,
                           trajectory=trajectory)

        # Lanes editor mode
        elif (self.editorMode == self.ModeEditorLane):
            isExists = False
            # Check if lane with name exists at the moment
            for i in range(len(self.lanes)):
                if (self.lanes[i]['name'] == self.editorModeArgument['name']):
                    isExists = True
                    break

            # Add only if not exists
            if (not isExists):
                self.__addLane(self.editorModeArgument['name'],
                               self.editorModeArgument['id'],
                               trajectory)

        # ROI editor mode
        elif (self.editorMode == self.ModeEditorROI):
            # TODO getting classes
            self.__addRoi(None,
                          classes=self.editorModeArgument,
                          trajectory=trajectory)
        # Distance editor mode
        elif (self.editorMode == self.ModeEditorDistance):
            isExists = False
            # Too few mouse clicks
            if (len(self.mouseClicks) != 4):
                isExists = True

            # Check if distance with name exists at the moment
            for i in range(len(self.distances)):
                if (self.distances[i]['id'] == self.editorModeArgument['id']):
                    isExists = True
                    break

            # Add only if not exists
            if (not isExists):
                self.__addDistance(self.editorModeArgument['id'],
                                   self.editorModeArgument['distance'],
                                   trajectory)
        # Framing editor mode
        elif (self.editorMode == self.ModeEditorFraming):
            ''' Do nothing '''
        # Obstacle editor mode
        elif (self.editorMode == self.ModeEditorObstacle):
            self.__addObstacle(trajectory=trajectory)

        previousMode = self.editorMode
        self.__resetEditorMode()
        self.update()

        # Emit signal
        self.signalEditorFinished.emit(previousMode)

    def paintEvent(self, event):
        ''' Draw on every paint event.'''
        # Get Preview info width & height
        width, height = self.rect().getRect()[2:]
        # Create painter
        widgetPainter = QPainter()
        widgetPainter.begin(self)

        # If image is loaded?
        if (self.imageBg is not None):
            # If framing then frame image?
            if (self.framing.IsFrame()):
                image = self.framing.GetFramedImage(self.imageBg)
            else:
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
                                   'No imagePath loaded!')

        # Editor mode - realtime drawing road
        if (self.editorMode == self.ModeEditorArea) and (len(self.mouseClicks) > 1):
            QDrawPolygon(widgetPainter, self.mouseClicks,
                         Qt.black, Qt.red, Qt.CrossPattern)

        # Editor mode - realtime drawing lane
        elif (self.editorMode == self.ModeEditorLane) and (len(self.mouseClicks) > 1):
            QDrawPolyline(widgetPainter, self.mouseClicks,
                          Qt.black, 1.0, 2)
        # Editor mode - realtime drawing distance
        elif (self.editorMode == self.ModeEditorDistance) and (len(self.mouseClicks) > 1):
            # Draw joints
            QDrawJoints(widgetPainter, self.mouseClicks, 5, Qt.black,
                        Qt.red, Qt.SolidPattern, 0.5)
            # Draw first line
            if (len(self.mouseClicks) >= 2):
                QDrawPolyline(
                    widgetPainter, self.mouseClicks[0:2], Qt.green, 1.0, 2, penStyle=Qt.DashLine)
            # Draw second line
            if (len(self.mouseClicks) == 4):
                QDrawPolyline(
                    widgetPainter, self.mouseClicks[2:4], Qt.green, 1.0, 2, penStyle=Qt.DashLine)

        # Editor mode - realtime drawing ROI
        elif (self.editorMode == self.ModeEditorROI) and (len(self.mouseClicks) > 0):
            QDrawJoints(widgetPainter, self.mouseClicks, 5, Qt.black,
                        Qt.red, Qt.SolidPattern, 0.5)
            if (len(self.mouseClicks) > 1):
                QDrawPolyline(widgetPainter, self.mouseClicks,
                              Qt.black, 1.0, 2)

        # Editor mode - realtime drawing framing
        elif (self.editorMode == self.ModeEditorFraming):
            # Draw framing
            if (self.framing.IsFrame()):
                # Get center and top right and calculate all points
                xc, yc = self.framing.GetCenterToView()
                width = self.framing.GetWidthToView()
                height = self.framing.GetHeightToView()
                # Draw rectangle
                rect = CreateRectangle(xc, yc, width, height)
                QDrawPolygon(widgetPainter,
                             rect,
                             brushColor=Qt.white,
                             brushStyle=Qt.SolidPattern,
                             brushOpacity=0.5
                             )
                # Draw joints
                points = self.framing.GetRectToView()
                points = [QPoint(point[0], point[1]) for point in points]
                QDrawJoints(widgetPainter,
                            points,
                            pen=Qt.green,
                            brushColor=Qt.white,
                            brushStyle=Qt.SolidPattern,
                            brushOpacity=0.5
                            )
        # Editor mode realtime drawing obstacles
        elif (self.editorMode == self.ModeEditorObstacle) and (len(self.mouseClicks) == 1):
            rect = [self.mouseClicks[0], QPoint(
                self.mouseCoords.x(), self.mouseCoords.y())]
            QDrawRectangle(widgetPainter, rect, pen=Qt.gray,
                           brushColor=Qt.green, brushStyle=Qt.SolidPattern, brushOpacity=0.25)

        widgetPainter.end()
