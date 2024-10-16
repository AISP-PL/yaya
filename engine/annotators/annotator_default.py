"""
 Default annotator class.
"""

from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtGui import QColor
from engine.annote_enums import AnnoteAuthorType, AnnoteEvaluation
import helpers.boxes as boxes
from helpers.QtDrawing import QDrawElipse, QDrawRectangle, QDrawText, TextAlignment


class AnnotatorDefault:
    """Default annotator class."""

    @staticmethod
    def Draw(self, painter, highlight=False, isConfidence=True, isLabel=True):
        """Draw self."""
        width, height = painter.window().getRect()[2:]
        x1, y1, x2, y2 = boxes.ToAbsolute(self.box, width, height)

        # Label text
        label = self.className
        # Thicknes of border
        thickness = 1
        if highlight is True:
            thickness = 2

        # Brush opacity : Default 0.25
        brush_opacity: float = 0.25

        # Human orignal from file detection
        if self.authorType == AnnoteAuthorType.byHuman:
            if self.evalution in [
                AnnoteEvaluation.noEvaluation,
                AnnoteEvaluation.TruePositiveLabel,
            ]:
                brush_color = Qt.black
            elif self.evalution == AnnoteEvaluation.TruePositive:
                brush_color = Qt.darkYellow
            elif self.evalution == AnnoteEvaluation.FalseNegative:
                brush_color = Qt.red

        # Created by detector YOLO
        elif self.authorType == AnnoteAuthorType.byDetector:
            brush_color = QColor(0, 200, 0)
            brush_opacity = 0.6
            label = "{}".format(self.className)
            # If confidence drawing enabled
            if isConfidence:
                label += "[{:.2f}]".format(float(self.confidence))

        # Created by hand
        elif self.authorType == AnnoteAuthorType.byHand:
            brush_color = Qt.darkGreen
            brush_opacity = 0.6

        # Draw rectangle box
        QDrawRectangle(
            painter,
            [QPoint(x1, y1), QPoint(x2, y2)],
            pen=brush_color,
            penThickness=thickness,
            brushColor=brush_color,
            brushOpacity=brush_opacity,
        )

        # Text
        if isLabel:
            QDrawText(
                painter=painter,
                point=QPoint(x1, y1),
                text=label,
                bgColor=brush_color,
                textAlign=TextAlignment.Center,
            )

        # Author Human : Draw green circle in the center
        if self.authorType == AnnoteAuthorType.byHuman:
            xc, yc = (x1 + x2) // 2, (y1 + y2) // 2
            QDrawElipse(
                painter=painter,
                point=QPoint(xc, yc),
                radius=10,
                brushColor=Qt.green,
                brushStyle=Qt.SolidPattern,
            )
