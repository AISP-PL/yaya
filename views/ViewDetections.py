"""
    View
"""

from PyQt5 import QtCore
from PyQt5.QtWidgets import QTableWidget
from tqdm import tqdm

from PyQt5.QtWidgets import QTableWidgetItem

from Gui.widgets.EvalTableWidgetItem import EvaluationTableWidgetItem
from Gui.widgets.FloatTableWidgetItem import FloatTableWidgetItem
from Gui.widgets.HsvTableWidgetItem import HsvTableWidgetItem
from Gui.widgets.ImageTableWidgetItem import ImageTableWidgetItem
from Gui.widgets.PercentTableWidgetItem import PercentTableWidgetItem
from Gui.widgets.RectTableWidgetItem import RectTableWidgetItem
from engine.annote import Annote
from helpers.visuals import Visuals
from PyQt5.QtGui import QColor


class ViewDetections:
    """View of detections"""

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
        annotations_total = sum([len(file["Detections"]) for file in files])

        # Update GUI data
        table.clear()
        labels = _translate(
            "ViewDetections",
            "File/ID;Cat;Conf;Size;Ratio;Area;Hue;Saturation;Brightness",
        ).split(";")
        table.setSortingEnabled(False)
        table.setColumnCount(len(labels))
        table.setHorizontalHeaderLabels(labels)
        table.setRowCount(annotations_total)

        # Rows : View each row in a loop
        row_index = 0
        for fileEntry in tqdm(files, desc="Annotations view creation"):
            annotations: list[Annote] = fileEntry["Detections"]
            visuals: Visuals = fileEntry["Visuals"]

            for index, annotation in enumerate(annotations):

                # Start from column zero
                colIndex = 0

                # Column : Filename + Image
                item = ImageTableWidgetItem(
                    imagePath=fileEntry["Path"],
                    text=f"{fileEntry['Name']}_{index}",
                    image_crop=annotation.xyxy_px(visuals.width, visuals.height),
                    data=(fileEntry["ID"], index),
                    fontSize=14,
                    fontColor=QColor("#009970"),
                    fontUnderline=True,
                )
                table.setItem(row_index, colIndex, item)
                colIndex += 1

                # Column : Category
                item = QTableWidgetItem(str(annotation.className))
                table.setItem(row_index, colIndex, item)
                colIndex += 1

                # Column : Confidence of evaluation
                item = PercentTableWidgetItem(
                    annotation.evaluation_confidence, is_color=True
                )
                table.setItem(row_index, colIndex, item)
                colIndex += 1

                # Column : Size
                item = RectTableWidgetItem(
                    annotation.width_px(visuals.width),
                    annotation.height_px(visuals.height),
                    decimals=2,
                )
                table.setItem(row_index, colIndex, item)
                colIndex += 1

                # Column : Ratio w/h
                item = FloatTableWidgetItem(
                    annotation.width_px(visuals.width)
                    / annotation.height_px(visuals.height),
                    decimals=2,
                )
                table.setItem(row_index, colIndex, item)
                colIndex += 1

                # Column : Area
                item = FloatTableWidgetItem(
                    annotation.area_px(visuals.width, visuals.height), decimals=2
                )
                table.setItem(row_index, colIndex, item)
                colIndex += 1

                # Hue column
                item = HsvTableWidgetItem(hue=annotation.hue, value=annotation.hue)
                table.setItem(row_index, colIndex, item)
                colIndex += 1

                # Saturation column
                item = HsvTableWidgetItem(
                    hue=300,
                    saturation=annotation.saturation,
                    brightness=255,
                    value=annotation.saturation,
                )
                table.setItem(row_index, colIndex, item)
                colIndex += 1

                # Brightness column
                item = HsvTableWidgetItem(
                    saturation=0,
                    brightness=annotation.brightness,
                    value=annotation.brightness,
                )
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

        table.setMouseTracking(True)

        table.itemEntered.connect(ViewDetections.show_custom_tooltip)

    @staticmethod
    def show_custom_tooltip(item: QTableWidgetItem) -> None:
        """Show custom tooltip for ImageTableWidgetItem"""
        if isinstance(item, ImageTableWidgetItem):
            item.setToolTip(item.generate_tooltip())
