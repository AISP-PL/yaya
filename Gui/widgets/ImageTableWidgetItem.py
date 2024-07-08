"""
Created on 14 gru 2022

@author: spasz
"""

import os

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QColor, QIcon


class ImageTableWidgetItem(QtWidgets.QTableWidgetItem):

    def __init__(
        self,
        imagePath: str = None,
        text: str = "",
        data: str = None,
        fontSize: int = None,
        fontColor: QColor = None,
        backgroundColor: QColor = None,
        fontUnderline: bool = False,
        tooltipImageWidth: int = 640,
    ):
        """Constructor."""
        # QIcon : Load if possible
        qicon = None
        if (imagePath is not None) and (os.path.exists(imagePath)):
            # qicon = QIcon(imagePath)
            """Removed"""

        # Constructor variant with QIcon
        if qicon is not None:
            super().__init__(qicon, text)
        # Constructor variant without QIcon
        else:
            super().__init__(text)

        # Image/Icon tooltip : Add if icon is loaded (file exists)
        if (imagePath is not None) and (qicon is not None):
            self.setToolTip(
                f"<img src='{imagePath}' width='{tooltipImageWidth}'><BR><h2>{text}</h2>"
            )

        # Data : Add
        self.setData(QtCore.Qt.UserRole, data)

        if fontSize is not None:
            font = self.font()
            font.setPixelSize(fontSize)
            self.setFont(font)

        if fontColor is not None:
            self.setForeground(fontColor)

        if backgroundColor is not None:
            self.setBackground(backgroundColor)

        if fontUnderline:
            font = self.font()
            font.setUnderline(True)
            self.setFont(font)
