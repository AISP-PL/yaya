"""
Created on 14 gru 2022

@author: spasz
"""

from PyQt5 import QtCore, QtWidgets

from engine.annote import Annote


class AnnotationsTableWidgetItem(QtWidgets.QTableWidgetItem):
    # value
    value: int = 0

    def __init__(self, annotations: list[Annote]):
        """Constructor."""
        super().__init__()

        # Text as string
        text = ",".join({f"{item.classNumber}" for item in annotations})
        self.setText(text)

        # Value : Numer of annotations
        self.value = len(annotations)

        # Set item data
        self.setData(QtCore.Qt.UserRole, self.value)

    def __lt__(self, other: QtWidgets.QTableWidgetItem):
        """Operation < for sorting."""
        value = other.data(QtCore.Qt.UserRole)
        return (value is not None) and (self.value < value)
