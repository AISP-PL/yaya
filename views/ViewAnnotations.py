"""
    View of annotations
"""

from PyQt5 import QtCore
from PyQt5.QtWidgets import QTableWidget
from tqdm import tqdm

from PyQt5.QtWidgets import QTableWidgetItem

from Gui.widgets.FloatTableWidgetItem import FloatTableWidgetItem
from Gui.widgets.RectTableWidgetItem import RectTableWidgetItem
from engine.annote import Annote


class ViewAnnotations:

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

        # Annotations : Calculate sum
        annotations_total = sum([len(file["Annotations"]) for file in files])

        # Update GUI data
        table.clear()
        labels = _translate("ViewAnnotations", "File/ID;Cat;Size;Area").split(";")
        table.setSortingEnabled(False)
        table.setColumnCount(len(labels))
        table.setHorizontalHeaderLabels(labels)
        table.setRowCount(annotations_total)

        # Rows : View each row in a loop
        row_index = 0
        for fileEntry in tqdm(files, desc="Annotations view creation"):
            annotations: list[Annote] = fileEntry["Annotations"]

            for index, annotation in enumerate(annotations):

                # Start from column zero
                colIndex = 0

                # Column : Filename + Image
                item = QTableWidgetItem(f"{fileEntry['Name']}_{index}")
                item.setToolTip('<img src="{}" width="480">'.format(fileEntry["Path"]))
                item.setData(QtCore.Qt.UserRole, fileEntry["ID"])
                table.setItem(row_index, colIndex, item)
                colIndex += 1

                # Column : Category
                item = QTableWidgetItem(str(annotation.className))
                item.setData(QtCore.Qt.UserRole, fileEntry["ID"])
                table.setItem(row_index, colIndex, item)
                colIndex += 1

                # Column : Size
                item = RectTableWidgetItem(
                    annotation.width, annotation.height, decimals=3
                )
                item.setData(QtCore.Qt.UserRole, fileEntry["ID"])
                table.setItem(row_index, colIndex, item)
                colIndex += 1

                # Column : Area
                item = FloatTableWidgetItem(annotation.area, decimals=3)
                item.setData(QtCore.Qt.UserRole, fileEntry["ID"])
                table.setItem(row_index, colIndex, item)
                colIndex += 1

                # Next row
                row_index += 1

        # GUI - Enable sorting again
        table.setIconSize(QtCore.QSize(96, 59))
        table.setColumnWidth(0, 100)
        table.setSortingEnabled(True)
        table.resizeColumnsToContents()
        table.resizeRowsToContents()
