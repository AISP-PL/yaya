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
        filter_classes: list[str] = None,
    ):
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
            "Name;ImSize;Annotated;Hue;Saturation;Brightness;ImHash;"
            + "Classes;Size;New dets;Correct;CorrectBbox;Precision;Recall;Errors;"
            + "Match.Confidence;Det.WorstConfidence",
        ).split(";")
        table.setColumnCount(len(labels))
        table.setHorizontalHeaderLabels(labels)
        table.setRowCount(len(files))
        table.setColumnCount(len(labels))

        # Rows : View each row in a loop
        for rowIndex, fileEntry in enumerate(tqdm(files, desc="Table view creation")):
            # Filter : Classes of annotations
            if (filter_classes is not None) or (len(filter_classes) > 0):
                if not any(
                    annotation.className in filter_classes
                    for annotation in fileEntry["Annotations"]
                ):
                    continue

            ViewImagesTableRow.View(table, rowIndex, fileEntry)

        # GUI - Enable sorting again
        table.setIconSize(QtCore.QSize(96, 59))
        table.setColumnWidth(0, 100)
        table.setSortingEnabled(True)
        table.resizeColumnsToContents()
        table.resizeRowsToContents()
