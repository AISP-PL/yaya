"""
Created on 14 gru 2022

@author: spasz
"""

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QColor


class HsvTableWidgetItem(QtWidgets.QTableWidgetItem):
    # Float value
    value: float = 0

    def __init__(
        self,
        hue: float = 0.0,
        saturation: float = 255,
        brightness: float = 128,
        value: float = 0,
    ):
        """
        HSV table widget item.

        Parameters
           ----------
           hue : float
               Hue value.
           saturation : float
               Saturation value.
           brightness : float
               Brightness value.

           decimals : int
               Number of decimal places.
           value : float
               Value of item converted to text.
        """
        super().__init__()

        if value is None or value == float("nan"):
            value = 0

        # Set variables
        self.value = value

        # Set item data
        self.setData(QtCore.Qt.UserRole, self.value)
        self.setText(f"{self.value:2.0f}")

        # Text alignment
        self.setTextAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)

        # Coloring : Set color by hue
        self.setBackground(
            QColor.fromHsv(round(hue), round(saturation), round(brightness))
        )

        # Foreground color : Set white or black, depending on brightness
        if brightness < 128:
            self.setForeground(QColor(255, 255, 255))
        else:
            self.setForeground(QColor(0, 0, 0))

    def __lt__(self, other: QtWidgets.QTableWidgetItem):
        """Operation < for sorting."""
        value = other.data(QtCore.Qt.UserRole)
        return (value is not None) and (self.value < value)
