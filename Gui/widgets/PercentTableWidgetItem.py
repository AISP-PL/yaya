"""
Created on 14 gru 2022

@author: spasz
"""

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QColor


class PercentTableWidgetItem(QtWidgets.QTableWidgetItem):
    # Float value
    value: float = 0

    def __init__(self, value: float = 0, is_color: bool = False):
        """Constructor."""
        super().__init__()
        # Set variables
        self.value = value

        # Set item data
        self.setData(QtCore.Qt.UserRole, value)
        self.setText(f"{self.value:.2f}%")
        self.setTextAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)

        # Coloring : Set color from 0% red through yellow to green 100%
        if is_color:
            value_float = value / 100
            if value_float < 0.5:
                self.setBackground(QColor(255, round(255 * value_float * 2), 0))
            else:
                self.setBackground(QColor(round(255 * (1 - value_float) * 2), 255, 0))

    def __lt__(self, other: QtWidgets.QTableWidgetItem):
        """Operation < for sorting."""
        value = other.data(QtCore.Qt.UserRole)
        return (value is not None) and (self.value < value)
