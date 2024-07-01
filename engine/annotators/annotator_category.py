"""
 Default annotator class.
"""

from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtGui import QColor

import helpers.boxes as boxes
from engine.annote import Annote
from engine.annote_enums import AnnoteAuthorType, AnnoteEvaluation
from helpers.QtDrawing import QDrawRectangle, QDrawText, TextAlignment
from helpers.colors import colorSchemeMatplotlib


class AnnotatorCategory:
    """Default annotator class."""

    @staticmethod
    def classnumber_to_color(class_number: int) -> tuple:
        """Get color based on class number."""
        scheme = colorSchemeMatplotlib
        return scheme[class_number % len(scheme)]

    @staticmethod
    def Draw(annote: Annote, painter, highlight=False, isConfidence=True, isLabel=True):
        """Draw self."""
        # Brush opacity : Default
        brush_opacity: float = 0.30
        # Get image size
        width, height = painter.window().getRect()[2:]
        # Get box coordinates
        x1, y1, x2, y2 = boxes.ToAbsolute(annote.box, width, height)
        # Label text
        text_label = f"{annote.className}\n{annote.confidence:2.0f}%"
        # Confidence
        confidence = annote.confidence
        # Human orignal from file detection
        if annote.authorType == AnnoteAuthorType.byHuman:
            # Evalution : Missing or not detected.
            if annote.evalution in {
                AnnoteEvaluation.noEvaluation,
                AnnoteEvaluation.FalseNegative,
            }:
                confidence = 0
                text_label = f"{annote.className}[X]"
            # Evalution :  Perfect match and label
            elif annote.evalution == AnnoteEvaluation.TruePositiveLabel:
                confidence = annote.confidence
                text_label += "[OK]"
            # Evalution :  Perfect match box but not label
            elif annote.evalution == AnnoteEvaluation.TruePositive:
                confidence = min(50, confidence)
                text_label += "[~]"

        # Brush color : Depends on category
        b, g, r = AnnotatorCategory.classnumber_to_color(annote.classNumber)
        brush_color = QColor(r, g, b)

        # Pen properties  : Depends on author type
        if annote.authorType in {AnnoteAuthorType.byHuman, AnnoteAuthorType.byHand}:
            pen_color = Qt.black
            text_color = Qt.black
            pen_thickness = 2
        elif annote.authorType == AnnoteAuthorType.byDetector:
            pen_color = brush_color
            text_color = Qt.white
            pen_thickness = 2

        # Draw rectangle box
        QDrawRectangle(
            painter,
            [QPoint(x1, y1), QPoint(x2, y2)],
            pen=pen_color,
            penThickness=pen_thickness,
            brushColor=brush_color,
            brushOpacity=brush_opacity,
        )

        # Text
        if isLabel or isConfidence:
            # Position : Center of the box
            xc = (x1 + x2) // 2
            yc = (y1 + y2) // 2

            QDrawText(
                painter=painter,
                point=QPoint(xc, yc),
                text=text_label,
                pen=text_color,
                bgColor=brush_color,
                textAlign=TextAlignment.Center,
            )
