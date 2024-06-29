"""
 Default annotator class.
"""

from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtGui import QColor

import helpers.boxes as boxes
from engine.annote import Annote
from engine.annote_enums import AnnoteAuthorType, AnnoteEvaluation
from helpers.QtDrawing import QDrawRectangle, QDrawText, TextAlignment


def RYG_color_as_rgb(value: float) -> tuple:
    """
    Get color based on value 0..100
    using red-yellow-green color scale.

    Parameters:
    -----------
    value : float
        Value 0..100.


    Returns:
    --------
    RGB color tuple.
    """
    value_float = min(1, value / 100)
    if value_float < 0.5:
        return (255, round(255 * value_float * 2), 0)

    return (round(255 * (1 - value_float) * 2), 255, 0)


class AnnotatorConfidenceHeat:
    """Default annotator class."""

    @staticmethod
    def Draw(annote: Annote, painter, highlight=False, isConfidence=True, isLabel=True):
        """Draw self."""
        # Brush opacity : Default 0.25
        brush_opacity: float = 0.25
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

        # Brush color
        r, g, b = RYG_color_as_rgb(confidence)
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
