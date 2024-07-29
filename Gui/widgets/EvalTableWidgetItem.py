"""
Created on 14 gru 2022

@author: spasz
"""

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QColor

from engine.annote_enums import AnnoteEvaluation


class EvaluationTableWidgetItem(QtWidgets.QTableWidgetItem):
    # value
    value: AnnoteEvaluation

    def __init__(self, value: AnnoteEvaluation):
        """Constructor."""
        super().__init__()
        # Set variables
        self.value = value

        # Set item data
        self.setData(QtCore.Qt.UserRole, value)

        # Text formatting
        self.setText(self.value.name)
        self.setTextAlignment(QtCore.Qt.AlignCenter)

        # TPL : Green
        if self.value == AnnoteEvaluation.TruePositiveLabel:
            self.setBackground(QColor("#009970"))
        # TP : Light green
        elif self.value == AnnoteEvaluation.TruePositive:
            self.setBackground(QColor("#00CC99"))
        # FN : Red
        elif self.value == AnnoteEvaluation.FalseNegative:
            self.setBackground(QColor("#990000"))
        # No Evaluation : light blue
        else:
            self.setBackground(QColor("#99CCFF"))
