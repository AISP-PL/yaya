"""
    View of images QTableWidget.
"""

import logging

from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem

from Gui.widgets.FloatTableWidgetItem import FloatTableWidgetItem
from Gui.widgets.HueTableWidgetItem import HsvTableWidgetItem
from Gui.widgets.PercentTableWidgetItem import PercentTableWidgetItem
from Gui.widgets.RectTableWidgetItem import RectTableWidgetItem


class ViewImagesTableRow:

    @staticmethod
    def View(table: QTableWidget, rowIndex: int, fileEntry: dict):
        """View images in table."""
        # Get translations
        _translate = QtCore.QCoreApplication.translate

        # Check : Invalid metrics
        if "Metrics" not in fileEntry:
            return
        # Metrics
        metrics = fileEntry["Metrics"]
        # Get visuals
        visuals = fileEntry["Visuals"]

        # Start from column zero
        colIndex = 0

        # Filename column
        item = QTableWidgetItem(str(fileEntry["Name"]))
        item.setToolTip(str(fileEntry["ID"]))
        table.setItem(rowIndex, colIndex, item)
        colIndex += 1

        # width, height
        item = RectTableWidgetItem(visuals.width, visuals.height, decimals=0)
        item.setToolTip(str(fileEntry["ID"]))
        table.setItem(rowIndex, colIndex, item)
        colIndex += 1

        # Hue column
        item = HsvTableWidgetItem(hue=visuals.hue, value=visuals.hue)
        item.setToolTip(str(fileEntry["ID"]))
        table.setItem(rowIndex, colIndex, item)
        colIndex += 1

        # Saturation column
        item = HsvTableWidgetItem(
            hue=300,
            saturation=visuals.saturation,
            brightness=255,
            value=visuals.saturation,
        )
        item.setToolTip(str(fileEntry["ID"]))
        table.setItem(rowIndex, colIndex, item)
        colIndex += 1

        # Brightness column
        item = HsvTableWidgetItem(
            saturation=0, brightness=visuals.brightness, value=visuals.brightness
        )
        item.setToolTip(str(fileEntry["ID"]))
        table.setItem(rowIndex, colIndex, item)
        colIndex += 1

        # Image hash column
        item = FloatTableWidgetItem(visuals.dhash, decimals=7)
        item.setToolTip(str(fileEntry["ID"]))
        if visuals.isDuplicate:
            item.setBackground(Qt.red)
        table.setItem(rowIndex, colIndex, item)
        colIndex += 1

        # IsAnnotation column
        item = QTableWidgetItem()
        if fileEntry["IsAnnotation"]:
            item.setBackground(Qt.green)
            item.setText(
                f"{fileEntry['IsAnnotation']} / {len(fileEntry['Annotations'])}"
            )
        else:
            item.setBackground(Qt.red)
            item.setText(f"{fileEntry['IsAnnotation']}")
        item.setToolTip(str(fileEntry["ID"]))
        table.setItem(rowIndex, colIndex, item)
        colIndex += 1

        # Annotation classes
        item = QTableWidgetItem()
        item.setText(fileEntry["AnnotationsClasses"])
        item.setToolTip(str(fileEntry["ID"]))
        table.setItem(rowIndex, colIndex, item)
        colIndex += 1

        # Average width, height, size
        item = RectTableWidgetItem(metrics.AvgWidth, metrics.AvgHeight)
        item.setToolTip(str(fileEntry["ID"]))
        table.setItem(rowIndex, colIndex, item)
        colIndex += 1

        # Correct [%]
        item = PercentTableWidgetItem(metrics.correct)
        item.setToolTip(str(fileEntry["ID"]))
        table.setItem(rowIndex, colIndex, item)
        colIndex += 1

        # Correct boxes [%]
        item = PercentTableWidgetItem(metrics.correct_bboxes)
        item.setToolTip(str(fileEntry["ID"]))
        table.setItem(rowIndex, colIndex, item)
        colIndex += 1

        # New detections [j]
        item = QTableWidgetItem(f"{metrics.new_detections}")
        item.setToolTip(str(fileEntry["ID"]))
        table.setItem(rowIndex, colIndex, item)
        colIndex += 1

        # Precision column
        item = FloatTableWidgetItem(metrics.precision)
        item.setToolTip(str(fileEntry["ID"]))
        table.setItem(rowIndex, colIndex, item)
        colIndex += 1

        # Recall column
        item = FloatTableWidgetItem(metrics.recall)
        item.setToolTip(str(fileEntry["ID"]))
        table.setItem(rowIndex, colIndex, item)
        colIndex += 1

        # Errors column
        item = QTableWidgetItem(str(fileEntry["Errors"]))
        item.setToolTip(str(fileEntry["ID"]))
        table.setItem(rowIndex, colIndex, item)
        colIndex += 1

        # Confidence of matches
        item = FloatTableWidgetItem(metrics.matches_confidence)
        item.setToolTip(str(fileEntry["ID"]))
        table.setItem(rowIndex, colIndex, item)
        colIndex += 1

        # Detector worst case confidence
        item = FloatTableWidgetItem(metrics.detections_confidence_min)
        item.setToolTip(str(fileEntry["ID"]))
        table.setItem(rowIndex, colIndex, item)
        colIndex += 1
