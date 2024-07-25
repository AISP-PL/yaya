"""
Created on 14 gru 2022

@author: spasz
"""

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QColor


class ImhashTableWidgetItem(QtWidgets.QTableWidgetItem):
    # Float value
    value: float = 0

    def __init__(self, image_similarity: float = 0.0, is_duplicated: bool = False):
        """ """
        super().__init__()
        # Set variables
        self.value = image_similarity

        # Set item data
        self.setData(QtCore.Qt.UserRole, self.value)

        # Create hash from image similarity
        image_hash_str = f"{int(image_similarity * (10**7))}"
        self.setText(image_hash_str)
        self.setTextAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)

        # Foreground color : Set black
        self.setForeground(QColor(0, 0, 0))

        if is_duplicated:
            # Background color : Set red
            self.setBackground(QColor(255, 0, 0))
            self.setData(QtCore.Qt.UserRole, -image_similarity)
            self.value = -image_similarity
            self.setText(f"[D]{image_hash_str}")
        else:
            # Coloring : Set color by hue
            self.setBackground(
                QColor.fromHsv(round(image_similarity * 255), round(255), round(255))
            )

    def __lt__(self, other: QtWidgets.QTableWidgetItem):
        """Operation < for sorting."""
        value = other.data(QtCore.Qt.UserRole)
        return (value is not None) and (self.value < value)
