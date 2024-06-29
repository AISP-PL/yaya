"""
 Default annotator class.
"""

from PyQt5.QtGui import QColor

from engine.annote import Annote
from PyQt5.QtCore import QPoint, Qt
from engine.annote_enums import AnnoteAuthorType
import helpers.boxes as boxes
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
        width, height = painter.window().getRect()[2:]
        x1, y1, x2, y2 = boxes.ToAbsolute(annote.box, width, height)

        # Pen properties  : Depends on author type
        if annote.authorType in {AnnoteAuthorType.byHuman, AnnoteAuthorType.byHand}:
            pen_color = Qt.black
            pen_thickness = 3
        elif annote.authorType == AnnoteAuthorType.byDetector:
            pen_color = Qt.white
            pen_thickness = 1

        # Brush opacity : Default 0.25
        brush_opacity: float = 0.25

        # Brush color
        r, g, b = RYG_color_as_rgb(annote.confidence)
        brushColor = QColor(r, g, b)

        # Draw rectangle box
        QDrawRectangle(
            painter,
            [QPoint(x1, y1), QPoint(x2, y2)],
            pen=pen_color,
            penThickness=pen_thickness,
            brushColor=brushColor,
            brushOpacity=brush_opacity,
        )

        # Text
        if isLabel or isConfidence:
            # Label text
            label = f"{annote.className}\n{annote.confidence:2.0f}%"

            # Position : Center of the box
            xc = (x1 + x2) // 2
            yc = (y1 + y2) // 2

            QDrawText(
                painter=painter,
                point=QPoint(xc, yc),
                text=label,
                bgColor=brushColor,
                textAlign=TextAlignment.Center,
            )
