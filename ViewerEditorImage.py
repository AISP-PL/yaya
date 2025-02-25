import logging
from enum import Enum
from typing import Any, List, Optional

import cv2
import numpy as np
from PyQt5.QtCore import QPoint, QPointF, Qt, pyqtSignal
from PyQt5.QtGui import QPainter, QPixmap, QTransform
from PyQt5.QtWidgets import QWidget

import helpers.boxes as boxes
from engine.annotators.annotator import Annotator
from engine.annote import Annote
from engine.annote_enums import AnnotatorType, AnnoteAuthorType
from helpers.boxes import IsInside, PointsToRect, PointToAbsolute, PointToRelative
from helpers.images import GetFixedFitToBox
from helpers.QtDrawing import (
    CvImage2QtImage,
    QDrawCrosshair,
    QDrawElipse,
    QDrawRectangle,
    QDrawTriangle,
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
    ImageScalingDynamicZoom = 3

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
        # Is thumbnail preview
        self.isThumbnail = True
        # Background image loaded
        self.image_bg = None
        # Mode of scaling image
        self.imageScaling = self.ImageScalingDynamicZoom
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

        self.imageScaling = (
            self.ImageScalingDynamicZoom
        )  # Ustawienie domyślnego trybu skalowania
        self.scale_factor = 1.0  # Współczynnik skalowania dla zoomu

        # Zmienne do obsługi przesuwania (panning)
        self._pan = False
        self._pan_start_x = 0
        self._pan_start_y = 0
        self._offset_x = 0
        self._offset_y = 0

        # Transformations :
        self.is_threshold = False
        self.is_sharpen = False
        self.is_clahe = False
        self.is_contrast = False

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

    def AbsoluteQTrajectoryToTrajectory(
        self, qtrajectory, width, height
    ) -> List[QPoint]:
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

    def mapToTransformed(self, point: QPoint) -> QPoint:
        """Mapuje punkt do układu współrzędnych po transformacji."""
        inv_transform = QTransform()
        inv_transform.translate(self._offset_x, self._offset_y)
        inv_transform.scale(self.scale_factor, self.scale_factor)
        inv_transform = inv_transform.inverted()[0]
        return inv_transform.map(point)

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

    def __autosetCursor(self, mode: int) -> None:
        """Auto set cursor based on editor mode"""
        # Cursor : Cross when adding annotation
        if mode == self.ModeAddAnnotation:
            self.setCursor(Qt.CrossCursor)
        # Cursor: Delete when removing annotation
        elif mode == self.ModeRemoveAnnotation:
            self.setCursor(Qt.ForbiddenCursor)
        # Cursor : Rename when renaming annotation
        elif mode == self.ModeRenameAnnotation:
            self.setCursor(Qt.IBeamCursor)
        else:
            self.setCursor(Qt.ArrowCursor)

    def SetEditorMode(self, mode: int, argument: Any = None) -> bool:
        """Sets editor mode."""
        self.__resetEditorMode()
        self.editorMode = mode
        self.editorModeArgument = argument
        self.__autosetCursor(self.editorMode)
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
        self.__autosetCursor(self.editorMode)

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
        self.image_bg = image
        self.scale_factor = 1.0
        self._pan = False
        self._pan_start_x = 0
        self._pan_start_y = 0
        self._offset_x = 0
        self._offset_y = 0
        self.update()

    def SetImageScaling(self, scalingMode):
        """Sets image scaling mode."""

    def GetImageSize(self) -> tuple[int, int]:
        """Returns ."""
        if self.image_bg is not None:
            height, width = self.image_bg.shape[0:2]
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

    def wheelEvent(self, event) -> None:
        """Obsługa zdarzenia przewijania myszy dla zoomu."""
        cursor_x = event.pos().x()
        cursor_y = event.pos().y()

        # Cursor position in image coordinates before scaling change
        img_pos_x = (cursor_x - self._offset_x) / self.scale_factor
        img_pos_y = (cursor_y - self._offset_y) / self.scale_factor

        delta = event.angleDelta().y()
        if delta > 0:
            self.scale_factor *= 1.1
        else:
            self.scale_factor /= 1.1

        # Limit scale factor
        self.scale_factor = max(0.1, min(self.scale_factor, 10))

        self._offset_x = cursor_x - img_pos_x * self.scale_factor
        self._offset_y = cursor_y - img_pos_y * self.scale_factor

        self.clamp_offsets()
        self.update()

    def clamp_offsets(self) -> None:
        """Clamp offsets to prevent scrolling out of bounds."""
        imWidth, imHeight = self.GetImageSize()
        viewportWidth = int(imWidth * self.scale_factor)
        viewportHeight = int(imHeight * self.scale_factor)
        widgetWidth, widgetHeight = self.GetViewSize()
        min_offset_x = widgetWidth - viewportWidth if viewportWidth > widgetWidth else 0
        max_offset_x = (
            0 if viewportWidth > widgetWidth else (widgetWidth - viewportWidth) // 2
        )
        min_offset_y = (
            widgetHeight - viewportHeight if viewportHeight > widgetHeight else 0
        )
        max_offset_y = (
            0 if viewportHeight > widgetHeight else (widgetHeight - viewportHeight) // 2
        )
        self._offset_x = min(max(self._offset_x, min_offset_x), max_offset_x)
        self._offset_y = min(max(self._offset_y, min_offset_y), max_offset_y)

    def mouseMoveEvent(self, event):
        """Handle mouse move event."""
        self.mousePosition = event.pos()
        if self.mouseTrajectory is not None:
            self.mouseTrajectory.append(event.pos())

        if self._pan:
            dx = event.x() - self._pan_start_x
            dy = event.y() - self._pan_start_y
            self._offset_x += dx
            self._offset_y += dy
            self._pan_start_x = event.x()
            self._pan_start_y = event.y()
            self.clamp_offsets()

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
                transf_point = self.mapToTransformed(QPoint(x, y))
                viewWidth, viewHeight = self.GetViewSize()
                toDelete = self.GetHoveredAnnotation(
                    boxes.PointToRelative(
                        (transf_point.x(), transf_point.y()), viewWidth, viewHeight
                    )
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
                transf_point = self.mapToTransformed(QPoint(x, y))
                viewWidth, viewHeight = self.GetViewSize()
                toDelete = self.GetHoveredAnnotation(
                    boxes.PointToRelative(
                        (transf_point.x(), transf_point.y()), viewWidth, viewHeight
                    )
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
                transf_point = self.mapToTransformed(QPoint(x, y))
                viewWidth, viewHeight = self.GetViewSize()
                toDelete = self.GetHoveredAnnotation(
                    boxes.PointToRelative(
                        (transf_point.x(), transf_point.y()), viewWidth, viewHeight
                    )
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

        if event.button() == Qt.LeftButton and self._pan:
            self._pan = False
            self.setCursor(Qt.ArrowCursor)
            return

        super().mouseReleaseEvent(event)

    def CallbackEditorFinished(
        self, mouse_button: MouseButton = MouseButton.NoButton
    ) -> None:
        """Finished editor mode."""
        # Get Preview info width & height
        widgetWidth, widgetHeight = self.GetViewSize()
        # Get image width & height
        imWidth, imHeight = self.GetImageSize()

        # Resize
        viewportWidth, viewportHeight = widgetWidth, widgetHeight

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

                # Zoom transform of clicks
                transformed_clicks = [
                    self.mapToTransformed(point) for point in self.mouseClicks
                ]

                # Mouse clicks to relative
                clicks_rel = self.AbsoluteQTrajectoryToTrajectory(
                    transformed_clicks, viewportWidth, viewportHeight
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
                # Zoom transform of clicks
                transformed_clicks = [
                    self.mapToTransformed(point) for point in self.mouseTrajectory
                ]
                trajectoryRel = self.AbsoluteQTrajectoryToTrajectory(
                    transformed_clicks, viewportWidth, viewportHeight
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
        height = abs(y2 - y1)
        size = min(max(10, height // 10), 40)
        xc = (x1 + x2) // 2
        yc = y1 - size

        # Draw : Red pointin triangle
        QDrawTriangle(
            painter=painter,
            point=QPoint(xc, yc),
            angle=90,
            size=size,
            pen=Qt.red,
            brushColor=Qt.red,
        )

    def paintEvent(self, event) -> None:
        """Draw on every paint event."""
        # Get Preview info width & height
        widgetWidth, widgetHeight = self.GetViewSize()
        # Create painter
        widgetPainter = QPainter(self)

        # If image is loaded?
        if self.image_bg is not None:
            # Setup image width & height
            imHeight, imWidth = self.image_bg.shape[0:2]
            image = self.image_bg
        # If there is no image then fill Black and draw text
        else:
            # Setup image width & height
            imWidth, imHeight = self.GetViewSize()
            image = np.zeros([imHeight, imWidth, 3], dtype=np.uint8)

        viewportWidth, viewportHeight = widgetWidth, widgetHeight

        # Save the current transformation
        widgetPainter.save()

        # Apply scaling and translation after drawing everything
        # Create a transform
        transform = QTransform()

        # Apply panning offsets
        transform.translate(self._offset_x, self._offset_y)
        # Apply scaling centered at the top-left corner (adjust if needed)
        transform.scale(self.scale_factor, self.scale_factor)

        # Set the transform to the painter
        widgetPainter.setTransform(transform)

        # Recalculate mouse position to viewport
        mousePosition = None
        if self.mousePosition is not None:
            # Adjust for scaling and translation
            inv_transform = widgetPainter.transform().inverted()[0]
            mapped_point = inv_transform.map(self.mousePosition)
            mousePosition = mapped_point

        # Recalculate mouse clicks to viewport
        mouseClicks = []
        if len(self.mouseClicks):
            inv_transform = widgetPainter.transform().inverted()[0]
            for mouseClick in self.mouseClicks:
                mapped_point = inv_transform.map(mouseClick)
                mouseClicks.append(mapped_point)

        # Transformations : Add if enabled
        if self.is_threshold:
            image = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY)[1]

        if self.is_clahe:
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            image = clahe.apply(image)
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

        if self.is_contrast:
            alpha = 1.5
            beta = 0
            image = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)
            # Apply sharpening filter
            kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
            image = cv2.filter2D(image, -1, kernel)

        if self.is_sharpen:
            kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
            image = cv2.filter2D(image, -1, kernel)

        # Draw current OpenCV image as pixmap
        pixmap = CvImage2QtImage(image)
        widgetPainter.drawPixmap(self.rect(), pixmap)

        # Draw miniature
        if self.isThumbnail:
            # Need to save and restore the transformation around drawing the miniature
            widgetPainter.save()
            widgetPainter.resetTransform()
            self.paintMiniature(widgetPainter, image)
            widgetPainter.restore()

        # Check : Annotations not hidden
        if not self.config["isAnnotationsHidden"]:

            # Annotations : Get
            annotations = self.annoter.GetAnnotations()

            # Sort by area (biggest first)
            annotations.sort(key=lambda x: x.area, reverse=True)

            # Draw : All annotations
            for index, annotate in enumerate(annotations):
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
                x = mousePosition.x()
                y = mousePosition.y()
                viewWidth, viewHeight = self.GetViewSize()
                rel_x, rel_y = boxes.PointToRelative((x, y), viewWidth, viewHeight)
                annote = self.GetHoveredAnnotation((rel_x, rel_y))
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

        # Draw crosshair : Only in specific modes
        if (mousePosition is not None) and self.editorMode in {self.ModeAddAnnotation}:
            QDrawCrosshair(
                widgetPainter,
                mousePosition.x(),
                mousePosition.y(),
                widgetWidth,
                widgetHeight,
                Qt.red,
            )

        # Restore the previous transformation
        widgetPainter.restore()
