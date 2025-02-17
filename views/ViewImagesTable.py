"""
    View of images QTableWidget.
"""

from PyQt5 import QtCore
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QHeaderView, QTableWidget
from tqdm import tqdm

from engine.annote_enums import AnnoteAuthorType
from Gui.widgets.AnnotationsTableWidgetItem import AnnotationsTableWidgetItem
from Gui.widgets.BoolTableWidgetItem import BoolTableWidgetItem
from Gui.widgets.FloatTableWidgetItem import FloatTableWidgetItem
from Gui.widgets.HsvTableWidgetItem import HsvTableWidgetItem
from Gui.widgets.ImageTableWidgetItem import ImageTableWidgetItem
from Gui.widgets.ImhashTableWidgetItem import ImhashTableWidgetItem
from Gui.widgets.PercentTableWidgetItem import PercentTableWidgetItem
from Gui.widgets.RectTableWidgetItem import RectTableWidgetItem
from Gui.widgets.StatTableWidgetItem import StatTableWidgetItem


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
            "Name;ImSize;Annotated;Validation;Correct;Classes;Dets;Time;Hue;Sat;Bri;ImHash;"
            + "IOU;OverlapIOU;Size;CorrectBbox;Precision;Recall;Errors;"
            + "Match.Confidence;Det.WorstConfidence",
        ).split(";")
        table.setSortingEnabled(False)
        table.setColumnCount(len(labels))
        table.setHorizontalHeaderLabels(labels)
        table.setRowCount(len(files))

        # Rows : View each row in a loop
        for rowIndex, fileEntry in enumerate(tqdm(files, desc="Table view creation")):
            ViewImagesTable.ViewRow(table, rowIndex, fileEntry)

        # GUI - Enable sorting again
        table.setIconSize(QtCore.QSize(96, 59))
        table.setColumnWidth(0, 100)
        table.setSortingEnabled(True)
        table.resizeColumnsToContents()

        # HSV columns fixed width
        header = table.horizontalHeader()
        header.setSectionResizeMode(7, QHeaderView.Fixed)
        header.setSectionResizeMode(8, QHeaderView.Fixed)
        header.setSectionResizeMode(9, QHeaderView.Fixed)
        table.setColumnWidth(7, 50)
        table.setColumnWidth(8, 50)
        table.setColumnWidth(9, 50)
        table.resizeRowsToContents()

    @staticmethod
    def ViewRow(
        table: QTableWidget,
        rowIndex: int,
        fileEntry: dict,
        isSelected: bool = False,
    ):
        """View images in table."""

        # Check : Invalid metrics
        if "Metrics" not in fileEntry:
            return
        # Metrics
        metrics = fileEntry["Metrics"]
        # Get visuals
        visuals = fileEntry["Visuals"]

        # Start from column zero
        colIndex = 0

        # Filename + Image : Color
        item = ImageTableWidgetItem(
            imagePath=fileEntry["Path"],
            text=fileEntry["Name"],
            data=str(fileEntry["ID"]),
            fontSize=14,
            fontColor=QColor("#009970"),
            fontUnderline=True,
        )
        item.setToolTip(str(fileEntry["ID"]))
        table.setItem(rowIndex, colIndex, item)
        colIndex += 1

        # width, height
        item = RectTableWidgetItem(visuals.width, visuals.height, decimals=0)
        item.setToolTip(str(fileEntry["ID"]))
        table.setItem(rowIndex, colIndex, item)
        colIndex += 1

        # IsAnnotation column
        item = BoolTableWidgetItem(fileEntry["IsAnnotation"])
        item.setToolTip(str(fileEntry["ID"]))
        table.setItem(rowIndex, colIndex, item)
        colIndex += 1

        # IsValidation dataset column
        item = BoolTableWidgetItem(fileEntry["IsValidation"])
        item.setToolTip(str(fileEntry["ID"]))
        table.setItem(rowIndex, colIndex, item)
        colIndex += 1

        # Correct [%]
        item = PercentTableWidgetItem(metrics.correct, is_color=True)
        item.setToolTip(str(fileEntry["ID"]))
        table.setItem(rowIndex, colIndex, item)
        colIndex += 1

        # Annotation classes
        item = AnnotationsTableWidgetItem(
            fileEntry["Annotations"], filter_auth=AnnoteAuthorType.byHuman
        )
        item.setToolTip(str(fileEntry["ID"]))
        table.setItem(rowIndex, colIndex, item)
        colIndex += 1

        # New detections [j]
        item = AnnotationsTableWidgetItem(
            metrics.new_detections, filter_auth=AnnoteAuthorType.byDetector
        )
        item.setToolTip(str(fileEntry["ID"]))
        table.setItem(rowIndex, colIndex, item)
        colIndex += 1

        # Timestamp from now
        item = StatTableWidgetItem(fileEntry["Datetime"])
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
        item = ImhashTableWidgetItem(visuals.dhash, visuals.isDuplicate)
        item.setToolTip(str(fileEntry["ID"]))
        table.setItem(rowIndex, colIndex, item)
        colIndex += 1

        # Average IOU
        item = PercentTableWidgetItem(100 * metrics.iou_avg, is_color=True)
        item.setToolTip(str(fileEntry["ID"]))
        table.setItem(rowIndex, colIndex, item)
        colIndex += 1

        # Overlappping IOU
        item = PercentTableWidgetItem(100 * metrics.overlapping_iou, is_color=True)
        item.setToolTip(str(fileEntry["ID"]))
        table.setItem(rowIndex, colIndex, item)
        colIndex += 1

        # Average width, height, size
        item = RectTableWidgetItem(metrics.AvgWidth, metrics.AvgHeight)
        item.setToolTip(str(fileEntry["ID"]))
        table.setItem(rowIndex, colIndex, item)
        colIndex += 1

        # Correct boxes [%]
        item = PercentTableWidgetItem(metrics.correct_bboxes)
        item.setToolTip(str(fileEntry["ID"]))
        table.setItem(rowIndex, colIndex, item)
        colIndex += 1

        # Precision column
        item = PercentTableWidgetItem(100 * metrics.precision, is_color=True)
        item.setToolTip(str(fileEntry["ID"]))
        table.setItem(rowIndex, colIndex, item)
        colIndex += 1

        # Recall column
        item = PercentTableWidgetItem(100 * metrics.recall, is_color=True)
        item.setToolTip(str(fileEntry["ID"]))
        table.setItem(rowIndex, colIndex, item)
        colIndex += 1

        # Errors column
        item = FloatTableWidgetItem(fileEntry["Errors"], decimals=0)
        item.setToolTip(str(fileEntry["ID"]))
        table.setItem(rowIndex, colIndex, item)
        colIndex += 1

        # Confidence of matches
        item = PercentTableWidgetItem(metrics.matches_confidence, is_color=True)
        item.setToolTip(str(fileEntry["ID"]))
        table.setItem(rowIndex, colIndex, item)
        colIndex += 1

        # Detector worst case confidence
        item = PercentTableWidgetItem(metrics.detections_confidence_min, is_color=True)
        item.setToolTip(str(fileEntry["ID"]))
        table.setItem(rowIndex, colIndex, item)
        colIndex += 1

        # Selection : Set row as selected
        if isSelected:
            table.selectRow(rowIndex)
