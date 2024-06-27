"""
 Default annotator class.
"""

from PyQt5.QtCore import QPoint, Qt
from engine.annote_enums import AnnoteAuthorType, AnnoteEvaluation
import helpers.boxes as boxes
from helpers.QtDrawing import QDrawRectangle, QDrawText, TextAlignment


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
                brushColor = Qt.black
            elif self.evalution == AnnoteEvaluation.TruePositive:
                brushColor = Qt.darkYellow
            elif self.evalution == AnnoteEvaluation.FalseNegative:
                brushColor = Qt.red

        # Created by detector YOLO
        elif self.authorType == AnnoteAuthorType.byDetector:
            brushColor = Qt.darkBlue
            brush_opacity = 0.6
            label = "{}".format(self.className)
            # If confidence drawing enabled
            if isConfidence:
                label += "[{:.2f}]".format(float(self.confidence))

        # Created by hand
        elif self.authorType == AnnoteAuthorType.byHand:
            brushColor = Qt.darkGreen
            brush_opacity = 0.6

        # Draw rectangle box
        QDrawRectangle(
            painter,
            [QPoint(x1, y1), QPoint(x2, y2)],
            pen=brushColor,
            penThickness=thickness,
            brushColor=brushColor,
            brushOpacity=brush_opacity,
        )

        # Text
        if isLabel:
            QDrawText(
                painter=painter,
                point=QPoint(x1, y1),
                text=label,
                bgColor=brushColor,
                textAlign=TextAlignment.Center,
            )
