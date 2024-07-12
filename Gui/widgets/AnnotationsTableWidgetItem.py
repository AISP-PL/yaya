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

        # Count classes occurences
        class_counts = {}
        for item in annotations:
            counts = class_counts.get(item.classNumber, 0)
            class_counts[item.classNumber] = counts + 1

        # Class counter: Sort by class_id
        class_counts = dict(sorted(class_counts.items()))

        # Text : Create list of texts "N x class_id"
        texts = [f"{count} x {class_id}" for class_id, count in class_counts.items()]
        text = "\n".join(texts)
        self.setText(text)
        self.setTextAlignment(QtCore.Qt.AlignCenter)

        # Value : Numer of annotations
        self.value = len(annotations)

        # Set item data
        self.setData(QtCore.Qt.UserRole, self.value)

    def __lt__(self, other: QtWidgets.QTableWidgetItem):
        """Operation < for sorting."""
        value = other.data(QtCore.Qt.UserRole)
        return (value is not None) and (self.value < value)
