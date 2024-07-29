"""
Created on 14 gru 2022

@author: spasz
"""

import os
from typing import Optional

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QColor, QIcon
import cv2


class ImageTableWidgetItem(QtWidgets.QTableWidgetItem):
    """Image table item"""

    # Image path
    image_path: str
    # Image crop
    image_crop: tuple[float, float, float, float]

    def __init__(
        self,
        imagePath: str = None,
        image_crop: Optional[tuple[float, float, float, float]] = None,
        text: str = "",
        data: str = None,
        fontSize: int = None,
        fontColor: QColor = None,
        fontUnderline: bool = False,
    ):
        """Constructor."""
        super().__init__(text)

        self.image_path = imagePath
        self.image_crop = image_crop

        # Data : Add
        self.setData(QtCore.Qt.UserRole, data)

        if fontSize is not None:
            font = self.font()
            font.setPixelSize(fontSize)
            self.setFont(font)

        if fontColor is not None:
            self.setForeground(fontColor)

        if fontUnderline:
            font = self.font()
            font.setUnderline(True)
            self.setFont(font)

    def generate_tooltip(self, max_width: int = 640) -> str:
        """Generate tooltip for image"""
        # Check : Image path
        if self.image_path is None or len(self.image_path) == 0:
            return ""

        # Check : No crop
        if self.image_crop is None:
            return f"<img src='{self.image_path}' width='{max_width}'>"

        # Read image, crop and save temp/temp.png
        image = cv2.imread(self.image_path)
        x1, y1, x2, y2 = self.image_crop
        x1 = round(x1)
        y1 = round(y1)
        x2 = round(x2)
        y2 = round(y2)
        image_cropped = image[y1:y2, x1:x2]
        cv2.imwrite("temp/temp.png", image_cropped)

        # Calculate max width
        cropped_max_width = min(max_width, x2 - x1)

        # Tooltip : Return
        return f"<img src='temp/temp.png' width='{cropped_max_width}'>"
