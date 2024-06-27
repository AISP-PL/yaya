"""
 Default annotator class.
"""

from PyQt5.QtCore import QPoint
from PyQt5.QtGui import QColor

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
    def Draw(self, painter, highlight=False, isConfidence=True, isLabel=True):
        """Draw self."""
        width, height = painter.window().getRect()[2:]
        x1, y1, x2, y2 = boxes.ToAbsolute(self.box, width, height)

        # Thicknes of border
        thickness = 1
        if highlight is True:
            thickness = 2

        # Brush opacity : Default 0.25
        brush_opacity: float = 0.25

        # Brush color
        r, g, b = RYG_color_as_rgb(self.confidence)
        brushColor = QColor(r, g, b)

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
        if isLabel or isConfidence:
            # Label text
            label = f"{self.className}\n{self.confidence:2.0f}%"

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
