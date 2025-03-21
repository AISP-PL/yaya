"""
 ImageTableWidgetItem.py with images buffer cropped creation.
"""

import logging
import os
from collections import deque
from typing import Optional

import cv2
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QColor


class ImageTableWidgetItem(QtWidgets.QTableWidgetItem):
    """Image table item"""

    # Image path
    image_path: str
    # Image crop
    image_crop: tuple[float, float, float, float]
    # Image prefix
    image_prefix: str
    # Cache dir
    cache_dir: str = "temp"
    # Image cropped cache
    cache = deque(maxlen=100)

    def __init__(
        self,
        imagePath: str = None,
        image_crop: Optional[tuple[float, float, float, float]] = None,
        image_prefix: str = "annotate",
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
        self.image_prefix = image_prefix

        # Image crop: If not None, then round
        if self.image_crop is not None:
            self.image_crop = tuple(round(x) for x in self.image_crop)

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

        # Tooltip : Autoset if no cropping
        if self.image_crop is None:
            self.setToolTip(self.generate_tooltip())

    def generate_tooltip(self, max_width: int = 320, max_height: int = 320) -> str:
        """Generate tooltip for image"""
        # Check : Image path
        if self.image_path is None or len(self.image_path) == 0:
            return ""

        # Check : No crop
        if self.image_crop is None:
            return f"<img src='{self.image_path}'>"

        # Cropped image : Generate hash
        x1, y1, x2, y2 = self.image_crop
        cache_key = (self.image_path, self.image_prefix, x1, y1, x2, y2)
        cached_file_path = os.path.join(self.cache_dir, f"{hash(cache_key)}.png")

        # Check : Hashed image not exists
        if cached_file_path not in self.cache:
            # Read image, crop and save temp/temp.png
            try:
                image = cv2.imread(self.image_path)
                x1, y1, x2, y2 = self.image_crop
                image_cropped = image[y1:y2, x1:x2]
                # Resize and preserve aspect ratio
                aspect_ratio = image_cropped.shape[1] / image_cropped.shape[0]
                if aspect_ratio > 1:
                    new_width = max_width
                    new_height = int(max_width / aspect_ratio)
                else:
                    new_width = int(max_height * aspect_ratio)
                    new_height = max_height

                image_cropped = cv2.resize(image_cropped, (new_width, new_height))
                cv2.imwrite(cached_file_path, image_cropped)

            except Exception as e:
                logging.error(f"Error cropping image: {e}")
                return ""

            # Cache : Append
            self.cache.append(cached_file_path)

            # Cache : Remove oldest
            if len(self.cache) > self.cache.maxlen:
                oldest_file = self.cache.popleft()
                if os.path.exists(oldest_file):
                    os.remove(oldest_file)

        # Tooltip : Return
        return f"<img src='{cached_file_path}'>"
