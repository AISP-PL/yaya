"""
    Detector image strategy enum
"""

from enum import Enum, auto


class ImageStrategy(Enum):
    """Different image strategies."""

    Rescale = "ImageRescale"
    LetterBox = "ImageLetterBox"
    Tiling = "ImageTiling"
