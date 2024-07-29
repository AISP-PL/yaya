"""
Created on 30 gru 2020

@author: spasz
"""

from enum import Enum
import logging
from typing import Any, Optional

import cv2
import numpy as np
from PyQt5.QtCore import QPointF, QPoint, Qt, pyqtSignal
from PyQt5.QtGui import QPainter, QPixmap, QPen
from PyQt5.QtWidgets import QWidget

from engine.annotators.annotator import Annotator
from engine.annote import Annote
import helpers.boxes as boxes
from engine.annote_enums import AnnotatorType, AnnoteAuthorType
from helpers.boxes import IsInside, PointsToRect, PointToAbsolute, PointToRelative
from helpers.images import GetFixedFitToBox
from helpers.QtDrawing import (
    CvImage2QtImage,
    QDrawCrosshair,
    QDrawElipse,
    QDrawRectangle,
)


class MouseButton(str, Enum):
    """Mouse button enum."""

    NoButton = "NoButton"
    LeftMouseButton = "LMB"
    RightMouseButton = "RMB"
    MiddleMouseButton = "MMB"
    ScrollUp = "ScrollUp"
    ScrollDown = "ScrollDown"


class ViewerEditorImage(QWidget):
    """States of editor."""

    # Editor mode
    ModeNone = 0
    ModeAddAnnotation = 1
    ModeRenameAnnotation = 2
    ModeRemoveAnnotation = 3
    ModePaintCircle = 4

    # Miniature position
    MiniatureLeft = 0
    MiniatureRight = 1

    # Image scaling mode
    ImageScalingResize = 0
    ImageScalingResizeAspectRatio = 1
    ImageScalingOriginalSize = 2

    # Image scaling algorithm
    ImageScalingLinear = 0
    ImageScalingNearest = 1

    # Define signals
    signalEditorFinished = pyqtSignal(int, name="EditorFinished")

    def __init__(self, parent):
        # QWidget constructor call
        super().__init__(parent=parent)

        # ----- Viewed data ------
        # Configuration
        self.config = {
            "isConfidence": True,
            "isAnnotationsHidden": False,
            "isLabelsHidden": False,
        }
        # Background image loaded
        self.imageBg = None
        # Mode of scaling image
        self.imageScaling = self.ImageScalingResize
        # Annoter for image
        self.annoter = None
        # Selected annotation index
        self.annotation_selected_id: Optional[int] = None
        # Annotator type for annotations
        self.annotator_type = AnnotatorType.Default
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
        # Miniature current position
        self.miniaturePosition = ViewerEditorImage.MiniatureLeft

        # UI init and show
        self.setMouseTracking(True)
        self.show()

    def set_annotator_type(self, annotator_type: AnnotatorType) -> None:
        """Set annotator type."""
        self.annotator_type = annotator_type

    def TrajectoryToAbsoluteQTrajectory(self, trajectory, width, height):
        """Recalculate trajectory to Q absolute trajectory."""
        qtrajectory = []
        for element in trajectory:
            x, y = PointToAbsolute((element[0], element[1]), width, height)
            qtrajectory.append(QPointF(x, y))

        return qtrajectory

    def AbsoluteQTrajectoryToTrajectory(self, qtrajectory, width, height):
        """Recalculate trajectory to Q absolute trajectory."""
        trajectory = []
        for qpoint in qtrajectory:
            x, y = qpoint.x(), qpoint.y()
            x, y = PointToRelative((x, y), width, height)
            trajectory.append((x, y))

        return trajectory

    def ItemQTrajectoryUpdate(self, item, width, height):
        """Update absolute Q trajectory in item."""
        item["QViewTrajectory"] = self.TrajectoryToAbsoluteQTrajectory(
            item["trajectory"], width, height
        )
        item["QViewWidth"] = width
        item["QViewHeight"] = height
        return item

    def GetOption(self, name):
        """Set configuration option."""
        if name in self.config:
            return self.config[name]

        return None

    def SetOption(self, name: str, value: bool):
        """Set configuration option."""
        if name in self.config:
            self.config[name] = value
            self.update()
        else:
            logging.error("(ViewerEditorImage) Unknown configuration option!")

    def SetClassNumber(self, index):
        """Set class number."""
        self.classNumber = index

    def SetEditorMode(self, mode, argument=None):
        """Sets editor mode."""
        self.__resetEditorMode()
        self.editorMode = mode
        self.editorModeArgument = argument
        return True

    def SetEditorModeArgument(self, argument):
        """Set/update editor mode argument."""
        self.editorModeArgument = argument

    def __resetEditorMode(self, defaultMode=ModeNone):
        """Resets editor mode."""
        self.mousePosition = None
        self.mouseTrajectory = None
        self.mouseClicks = []
        self.mouseDragging = False
        self.editorMode = defaultMode

    def SetAnnoter(self, annoter):
        """Set annoter handle."""
        if annoter is not None:
            self.annoter = annoter
            self.update()

    def SetImage(self, image: np.ndarray) -> None:
        """Set imagePath to show."""
        if image is None:
            logging.error("(ViewerEditorImage) Image is None!")
            return

        self.annotation_selected_id = None
        self.imageBg = image
        self.update()

    def SetImageScaling(self, scalingMode):
        """Sets image scaling mode."""
        self.imageScaling = scalingMode

    def GetImageSize(self):
        """Returns ."""
        if self.imageBg is not None:
            height, width = self.imageBg.shape[0:2]
            return width, height

        return 0, 0

    def GetViewSize(self):
        """Returns ."""
        width, height = self.rect().getRect()[2:]
        return width, height

    def GetHoveredAnnotation(self, point: tuple) -> Any:
        """Finds currently hovered annotation."""
        founded = None
        for element in self.annoter.GetAnnotations():
            # Check : Is inside
            if not element.IsInside(point):
                continue

            # Check : Is founded
            if founded is None:
                founded = element
                continue

            # Check : Area
            area1 = boxes.GetArea(element.GetBox())
            area2 = boxes.GetArea(founded.GetBox())
            if area1 < area2:
                founded = element

        return founded

    def SaveScreenshot(self, filepath: str) -> None:
        """Returns screenshot."""
        pixmap = QPixmap((self.size()))
        self.render(pixmap)
        pixmap.save(filepath)

    def ScreenshotToFile(self, path: str) -> bool:
        """Public method which renders widget to file."""
        # Render to pixmap of same width and height
        pixmap = self.grab(self.rect())
        # Save to filepath (return bool)
        return pixmap.save(path)

    def mouseMoveEvent(self, event):
        """Handle mouse move event."""
        self.mousePosition = event.pos()
        if self.mouseTrajectory is not None:
            self.mouseTrajectory.append(event.pos())

        self.update()

    def mousePressEvent(self, event):
        """Handle mouse event."""
        # Mode Add Annotation
        if self.editorMode == self.ModeAddAnnotation:
            # LPM adds point
            if event.buttons() == Qt.LeftButton:
                self.mouseClicks.append(event.pos())
                # If stored 2 points the call finish.
                if len(self.mouseClicks) >= 2:
                    self.CallbackEditorFinished(
                        mouse_button=MouseButton.LeftMouseButton
                    )

            # RPM cancels or removes
            elif event.buttons() == Qt.RightButton:
                if len(self.mouseClicks) > 0:
                    self.mouseClicks.clear()

                x, y = event.pos().x(), event.pos().y()
                viewWidth, viewHeight = self.GetViewSize()
                toDelete = self.GetHoveredAnnotation(
                    boxes.PointToRelative((x, y), viewWidth, viewHeight)
                )

                if toDelete is not None:
                    self.editorModeArgument = toDelete
                    self.CallbackEditorFinished(
                        mouse_button=MouseButton.RightMouseButton
                    )

        # Mode Rename Annotation
        elif self.editorMode == self.ModeRenameAnnotation:
            # LPM finds annotation
            if event.buttons() == Qt.LeftButton:
                x, y = event.pos().x(), event.pos().y()
                viewWidth, viewHeight = self.GetViewSize()
                toDelete = self.GetHoveredAnnotation(
                    boxes.PointToRelative((x, y), viewWidth, viewHeight)
                )
                # If clicked on annotation the return
                if toDelete is not None:
                    self.editorModeArgument = toDelete
                    self.CallbackEditorFinished(
                        mouse_button=MouseButton.LeftMouseButton
                    )

        # Mode Remove Annotation
        elif self.editorMode == self.ModeRemoveAnnotation:
            # LPM finds annotation
            if event.buttons() == Qt.LeftButton:
                x, y = event.pos().x(), event.pos().y()
                viewWidth, viewHeight = self.GetViewSize()
                toDelete = self.GetHoveredAnnotation(
                    boxes.PointToRelative((x, y), viewWidth, viewHeight)
                )

                # If clicked on annotation the return
                if toDelete is not None:
                    self.editorModeArgument = toDelete
                    self.CallbackEditorFinished(
                        mouse_button=MouseButton.LeftMouseButton
                    )

        # Mode Paint circle
        elif self.editorMode == self.ModePaintCircle:
            # LPM finds annotation
            if event.buttons() == Qt.LeftButton:
                # Enabled mouse trajectory storing
                self.mouseTrajectory = [event.pos()]

    def mouseReleaseEvent(self, event):
        """Handle mouse event."""
        # Mode Paint circle
        if self.editorMode == self.ModePaintCircle:
            self.CallbackEditorFinished(mouse_button=MouseButton.LeftMouseButton)

    def CallbackEditorFinished(
        self, mouse_button: MouseButton = MouseButton.NoButton
    ) -> None:
        """Finished editor mode."""
        # Get Preview info width & height
        widgetWidth, widgetHeight = self.GetViewSize()
        # Get image width & height
        imWidth, imHeight = self.GetImageSize()
        # ---------- Select scaling mode -----------
        # Resize
        if self.imageScaling == self.ImageScalingResize:
            viewportWidth, viewportHeight = widgetWidth, widgetHeight

        # Resize with aspect ratio
        elif self.imageScaling == self.ImageScalingResizeAspectRatio:
            viewportWidth, viewportHeight = GetFixedFitToBox(
                imWidth, imHeight, widgetWidth, widgetHeight
            )

        # Original size
        elif self.imageScaling == self.ImageScalingOriginalSize:
            viewportWidth, viewportHeight = imWidth, imHeight

        # Mode : Adding
        if self.editorMode == self.ModeAddAnnotation:
            # LPM :Add
            if mouse_button == MouseButton.LeftMouseButton:
                # Check : Clicks == 2
                if not len(self.mouseClicks) == 2:
                    return

                # Check : Clicks width & height > 10x10px
                width = abs(self.mouseClicks[0].x() - self.mouseClicks[1].x())
                height = abs(self.mouseClicks[0].y() - self.mouseClicks[1].y())
                if (width < 10) or (height < 10):
                    self.mouseClicks.clear()
                    return

                # Mouse clicks to relative
                clicks_rel = self.AbsoluteQTrajectoryToTrajectory(
                    self.mouseClicks, viewportWidth, viewportHeight
                )
                box = PointsToRect(clicks_rel[0], clicks_rel[1])
                self.annoter.AddAnnotation(box, self.classNumber)

            # RPM : Remove
            elif mouse_button == MouseButton.RightMouseButton:
                self.annoter.RemoveAnnotation(self.editorModeArgument)

        # Mode Rename Annotation
        elif self.editorMode == self.ModeRenameAnnotation:
            annote = self.editorModeArgument
            annote.SetClassNumber(self.classNumber)
            annote.SetAuthorType(AnnoteAuthorType.byHand)

        # Mode Remove Annotation
        elif self.editorMode == self.ModeRemoveAnnotation:
            self.annoter.RemoveAnnotation(self.editorModeArgument)

        # Mode Paint circle
        elif self.editorMode == self.ModePaintCircle:
            # Mouse trajectory relative
            trajectoryRel = []
            if self.mouseTrajectory is not None:
                trajectoryRel = self.AbsoluteQTrajectoryToTrajectory(
                    self.mouseTrajectory, viewportWidth, viewportHeight
                )

            imWidth, imHeight = self.GetImageSize()
            for relPoint in trajectoryRel:
                imPoint = PointToAbsolute(relPoint, imWidth, imHeight)
                # Add drawing to original image
                self.annoter.PaintCircles([imPoint], self.editorModeArgument, (0, 0, 0))

        previousMode = self.editorMode
        self.__resetEditorMode(previousMode)
        self.update()

        # Emit signal
        self.signalEditorFinished.emit(previousMode)

    def paintMiniature(
        self,
        painter: QPainter,
        image: np.array,
        miniWidth: int = 128,
        miniHeight: int = 128,
    ) -> None:
        """Painting miniature of image in painter."""
        # Get Preview info width & height
        widgetWidth, widgetHeight = self.GetViewSize()
        # Get image dimensions
        imHeight, imWidth = image.shape[0:2]
        # Get fitted image dimensions
        miniWidth, miniHeight = GetFixedFitToBox(
            imWidth, imHeight, miniWidth, miniHeight
        )
        # Change cv2 image to pixmap
        pixmap = CvImage2QtImage(cv2.resize(image, (miniWidth, miniHeight)))
        # Create position Qrect
        if self.miniaturePosition == ViewerEditorImage.MiniatureLeft:
            miniaturePosition = QPointF(0, 0)
        else:
            miniaturePosition = QPointF(widgetWidth - miniWidth, 0)

        # Check if mouse over miniature
        if self.mousePosition is not None:
            point = (self.mousePosition.x(), self.mousePosition.y())
            mx, my = miniaturePosition.x(), miniaturePosition.y()
            if IsInside(point, (mx, my, mx + miniWidth, my + miniHeight)):
                # Miniature position : Switch
                if self.miniaturePosition == ViewerEditorImage.MiniatureLeft:
                    self.miniaturePosition = ViewerEditorImage.MiniatureRight
                else:
                    self.miniaturePosition = ViewerEditorImage.MiniatureLeft

        # Draw on painter in QRect corner
        painter.drawPixmap(miniaturePosition, pixmap)

    def paint_selected(self, painter: QPainter, annote: Annote) -> None:
        """Draw selected annotation"""
        # Draw : Red selection circle
        viewWidth, viewHeight = self.GetViewSize()
        x1, y1, x2, y2 = boxes.ToAbsolute(annote.GetBox(), viewWidth, viewHeight)
        xc, yc = (x1 + x2) // 2, (y1 + y2) // 2
        radius = max(x2 - x1, y2 - y1) // 2

        # Draw : Red circle
        QDrawElipse(
            painter=painter,
            point=QPoint(xc, yc),
            radius=radius,
            pen=QPen(Qt.red, 10),
            brushOpacity=0.0,
        )

    def paintEvent(self, event):
        """Draw on every paint event."""
        # Get Preview info width & height
        widgetWidth, widgetHeight = self.GetViewSize()
        # Create painter
        widgetPainter = QPainter()
        widgetPainter.begin(self)

        # If image is loaded?
        if self.imageBg is not None:
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
        if self.imageScaling == self.ImageScalingResize:
            viewportWidth, viewportHeight = widgetWidth, widgetHeight

        # Resize with aspect ratio
        elif self.imageScaling == self.ImageScalingResizeAspectRatio:
            viewportWidth, viewportHeight = GetFixedFitToBox(
                imWidth, imHeight, widgetWidth, widgetHeight
            )
            widgetPainter.setViewport(0, 0, viewportWidth, viewportHeight)

        # Original size
        elif self.imageScaling == self.ImageScalingOriginalSize:
            widgetPainter.setViewport(0, 0, imWidth, imHeight)
            viewportWidth, viewportHeight = imWidth, imHeight

        # Recalculate mouse position to viewport
        mousePosition = None
        if self.mousePosition is not None:
            mx, my = boxes.PointToRelative(
                (self.mousePosition.x(), self.mousePosition.y()),
                viewportWidth,
                viewportHeight,
            )
            mousePosition = QPointF(mx * widgetWidth, my * widgetHeight)

        # Recalculate mouse clicks to viewport
        mouseClicks = []
        if len(self.mouseClicks):
            for mouseClick in self.mouseClicks:
                mx, my = boxes.PointToRelative(
                    (mouseClick.x(), mouseClick.y()), viewportWidth, viewportHeight
                )
                mouseClicks.append(QPointF(mx * widgetWidth, my * widgetHeight))

        # Draw current OpenCV image as pixmap
        pixmap = CvImage2QtImage(image)
        widgetPainter.drawPixmap(self.rect(), pixmap)

        # Draw miniature
        self.paintMiniature(widgetPainter, image)

        # Check : Annotations not hidden
        if not self.config["isAnnotationsHidden"]:

            # Draw : All annotations
            for index, annotate in enumerate(self.annoter.GetAnnotations()):
                Annotator.QtDraw(
                    annotate,
                    widgetPainter,
                    self.annotator_type,
                    isConfidence=True,
                    isLabel=not self.config["isLabelsHidden"],
                )

                # Check : index != selected
                if index != self.annotation_selected_id:
                    continue

                # Draw selected annotation
                self.paint_selected(widgetPainter, annotate)

            # Draw hovered annotation
            if mousePosition is not None:
                # Get hovered annotation
                annote = self.GetHoveredAnnotation(
                    boxes.PointToRelative(
                        (self.mousePosition.x(), self.mousePosition.y()),
                        viewportWidth,
                        viewportHeight,
                    )
                )
                if annote is not None:
                    Annotator.QtDraw(
                        annote,
                        widgetPainter,
                        self.annotator_type,
                        highlight=True,
                        isConfidence=True,
                        isLabel=True,
                    )

        # -------- Mode Annotation Draw -------
        if self.editorMode == self.ModeAddAnnotation:
            if (len(mouseClicks) != 0) and (mousePosition is not None):
                # Draw rectangle box
                QDrawRectangle(
                    widgetPainter,
                    [mouseClicks[0], mousePosition],
                    pen=Qt.green,
                    brushColor=Qt.green,
                    brushOpacity=0.1,
                )

        # -------- Mode Paint Draw -------
        if self.editorMode == self.ModePaintCircle:
            if mousePosition is not None:
                imWidth, imHeight = self.GetImageSize()
                radius = round((self.editorModeArgument / imWidth) * viewportWidth)
                QDrawElipse(widgetPainter, mousePosition, radius)

        # Draw crosshair
        if mousePosition is not None:
            QDrawCrosshair(
                widgetPainter,
                mousePosition.x(),
                mousePosition.y(),
                widgetWidth,
                widgetHeight,
                Qt.red,
            )

        widgetPainter.end()
