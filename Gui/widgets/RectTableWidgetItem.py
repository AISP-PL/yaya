"""
Created on 14 gru 2022

@author: spasz
"""

from PyQt5 import QtCore, QtWidgets


class RectTableWidgetItem(QtWidgets.QTableWidgetItem):
    # Width of rectangle
    width: int = 0
    # Height of rectangle
    height: int = 0

    def __init__(self, width: float = 0, height: float = 0, decimals: int = 2):
        """Constructor."""
        super().__init__()
        # Set variables
        self.width = width
        self.height = height

        # Set item data
        self.setData(QtCore.Qt.UserRole, self.width * self.height)
        self.setText(f"{self.width:2.{decimals}f} x {self.height:2.{decimals}f}")
        self.setTextAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)

    def __lt__(self, other: QtWidgets.QTableWidgetItem):
        """Operation < for sorting."""
        value = other.data(QtCore.Qt.UserRole)
        return (value is not None) and ((self.width * self.height) < value)
