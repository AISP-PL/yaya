'''
    View of images QTableWidget.
'''
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QAbstractItemView
from PyQt5 import QtCore
from PyQt5.QtCore import Qt

class ViewImagesTableRow:

    @staticmethod
    def View(table : QTableWidget, rowIndex:int, fileEntry : dict):
        ''' View images in table.'''
        # Get translations
        _translate = QtCore.QCoreApplication.translate
        # Metrics
        metrics = fileEntry['Metrics']
        
        # Start from column zero
        colIndex = 0

        # Filename column
        item = QTableWidgetItem(str(fileEntry['Name']))
        item.setToolTip(str(fileEntry['ID']))
        table.setItem(rowIndex, colIndex, item)
        colIndex += 1

        # IsAnnotation column
        item = QTableWidgetItem()
        if (fileEntry['IsAnnotation']):
            item.setBackground(Qt.green)
            item.setText(f"{fileEntry['IsAnnotation']} / {len(fileEntry['Annotations'])}")
        else:
            item.setBackground(Qt.red)
            item.setText(f"{fileEntry['IsAnnotation']}")
        item.setToolTip(str(fileEntry['ID']))
        table.setItem(rowIndex, colIndex, item)
        colIndex += 1
            
        # Correct [%]
        item = QTableWidgetItem(f"{metrics.correct:2.2f}%")
        item.setToolTip(str(fileEntry['ID']))
        table.setItem(rowIndex, colIndex, item)
        colIndex += 1

        # Correct boxes [%]
        item = QTableWidgetItem(f"{metrics.correct_bboxes:2.2f}%")
        item.setToolTip(str(fileEntry['ID']))
        table.setItem(rowIndex, colIndex, item)
        colIndex += 1

        # New detections [j]
        item = QTableWidgetItem(f"{metrics.new_detections}d")
        item.setToolTip(str(fileEntry['ID']))
        table.setItem(rowIndex, colIndex, item)
        colIndex += 1

        # Precision column
        item = QTableWidgetItem(f"{metrics.precision}")
        item.setToolTip(str(fileEntry['ID']))
        table.setItem(rowIndex, colIndex, item)
        colIndex += 1

        # Recall column
        item = QTableWidgetItem(f"{metrics.recall}")
        item.setToolTip(str(fileEntry['ID']))
        table.setItem(rowIndex, colIndex, item)
        colIndex += 1

        # Errors column
        item = QTableWidgetItem(str(fileEntry['Errors']))
        item.setToolTip(str(fileEntry['ID']))
        table.setItem(rowIndex, colIndex, item)
        colIndex += 1

        # GUI - Enable sorting again
        table.setSortingEnabled(True)
        table.resizeColumnsToContents()
        table.resizeRowsToContents()