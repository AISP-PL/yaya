"""
    Detector image strategy enum
"""

from enum import Enum, auto


class ImageStrategy(Enum):
    """Different image strategies."""

    Rescale = "ImageRescale"
    RescaleNearest = "ImageRescaleNearest"
    LetterBox = "ImageLetterBox"
    Tiling2x2 = "ImageTiling2x2"
    Tiling = "ImageTiling"
