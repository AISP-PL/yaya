"""
    View of images QTableWidget.
"""

from PyQt5 import QtCore
from PyQt5.QtWidgets import QTableWidget

from views.ViewImagesTableRow import ViewImagesTableRow


class ViewImagesTable:

    @staticmethod
    def View(table: QTableWidget, files: list):
        """View images in table."""
        # Check : Invalid files list
        if (files is None) or (len(files) == 0):
            return

        # Get translations
        _translate = QtCore.QCoreApplication.translate

        # Update GUI data
        table.clear()
        labels = _translate(
            "ViewImagesTable",
            "Name;ImSize;Hue;Saturation;Brightness;ImHash;"
            + "IsAnnotated;Classes;Size;Correct;CorrectBbox;New [j];Precision;Recall;Errors;"
            + "Match.Confidence;Det.WorstConfidence",
        ).split(";")
        table.setColumnCount(len(labels))
        table.setHorizontalHeaderLabels(labels)
        table.setRowCount(len(files))
        table.setColumnCount(len(labels))

        # Rows : View each row in a loop
        for rowIndex, fileEntry in enumerate(files):
            ViewImagesTableRow.View(table, rowIndex, fileEntry)

        # GUI - Enable sorting again
        table.setIconSize(QtCore.QSize(96, 59))
        table.setSortingEnabled(True)
        table.resizeColumnsToContents()
        table.resizeRowsToContents()
