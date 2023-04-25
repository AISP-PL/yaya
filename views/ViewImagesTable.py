'''
    View of images QTableWidget.
'''
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QAbstractItemView
from PyQt5.QtCore import Qt
from PyQt5 import QtCore

from views.ViewImagesTableRow import ViewImagesTableRow


class ViewImagesTable:

    @staticmethod
    def View(table: QTableWidget, files: list):
        ''' View images in table.'''
        # Get translations
        _translate = QtCore.QCoreApplication.translate

        # Update GUI data
        table.clear()
        labels = _translate('ViewImagesTable',
                            'Name;IsAnnotated;Correct [%];Correct [boxes][%];New [j];Precision;Recall;Hue;Saturation;Brightness;Errors').split(';')
        table.setColumnCount(len(labels))
        table.setHorizontalHeaderLabels(labels)
        table.setRowCount(len(files))
        table.setColumnCount(len(labels))

        # View each row.
        for rowIndex, fileEntry in enumerate(files):
            ViewImagesTableRow.View(table, rowIndex, fileEntry)

        # GUI - Enable sorting again
        table.setSortingEnabled(True)
        table.resizeColumnsToContents()
        table.resizeRowsToContents()
