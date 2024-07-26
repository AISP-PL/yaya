"""
    View of images QTableWidget.
"""

from PyQt5 import QtCore
from PyQt5.QtWidgets import QTableWidget
from tqdm import tqdm

from views.ViewImagesTableRow import ViewImagesTableRow


class ViewImagesTable:

    @staticmethod
    def View(
        table: QTableWidget,
        files: list,
    ):
        """View images in table."""
        # Check : Files, correct None
        if files is None:
            files = []

        # Get translations
        _translate = QtCore.QCoreApplication.translate

        # Update GUI data
        table.clear()
        labels = _translate(
            "ViewImagesTable",
            "Name;ImSize;Annotated;Validation;Correct;Classes;Time;Hue;Saturation;Brightness;ImHash;"
            + "Size;New dets;CorrectBbox;Precision;Recall;Errors;"
            + "Match.Confidence;Det.WorstConfidence",
        ).split(";")
        table.setSortingEnabled(False)
        table.setColumnCount(len(labels))
        table.setHorizontalHeaderLabels(labels)
        table.setRowCount(len(files))

        # Rows : View each row in a loop
        for rowIndex, fileEntry in enumerate(tqdm(files, desc="Table view creation")):
            ViewImagesTableRow.View(table, rowIndex, fileEntry)

        # GUI - Enable sorting again
        table.setIconSize(QtCore.QSize(96, 59))
        table.setColumnWidth(0, 100)
        table.setSortingEnabled(True)
        table.resizeColumnsToContents()
        table.resizeRowsToContents()
