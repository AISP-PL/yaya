"""
    View of annotations
"""

from PyQt5 import QtCore
from PyQt5.QtWidgets import QTableWidget
from tqdm import tqdm

from PyQt5.QtWidgets import QTableWidgetItem

from Gui.widgets.EvalTableWidgetItem import EvaluationTableWidgetItem
from Gui.widgets.FloatTableWidgetItem import FloatTableWidgetItem
from Gui.widgets.HsvTableWidgetItem import HsvTableWidgetItem
from Gui.widgets.PercentTableWidgetItem import PercentTableWidgetItem
from Gui.widgets.RectTableWidgetItem import RectTableWidgetItem
from engine.annote import Annote
from helpers.visuals import Visuals


class ViewAnnotations:
    """View of annotations"""

    @staticmethod
    def set_cropped_image_tooltip(
        item: QTableWidgetItem, image_path: str, xyxy: tuple[float, float, float, float]
    ) -> None:
        """Set tooltip for item with cropped image"""
        x1, y1, x2, y2 = xyxy
        x1 = round(x1)
        y1 = round(y1)
        x2 = round(x2)
        y2 = round(y2)
        width = x2 - x1
        height = y2 - y1
        tooltip = f"""
        <div style='width:{width}px; height:{height}px; overflow:hidden;'>
            <img src='{image_path}' style='position:absolute; max-width:{width}px; max-height:{height}px;  top:-{y1}px; left:-{x1}px;'>
        </div>
        """
        item.setToolTip(tooltip)

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
        labels = _translate(
            "ViewAnnotations",
            "File/ID;Cat;Conf;Eval;Size;Ratio;Area;Hue;Saturation;Brightness",
        ).split(";")
        table.setSortingEnabled(False)
        table.setColumnCount(len(labels))
        table.setHorizontalHeaderLabels(labels)
        table.setRowCount(annotations_total)

        # Rows : View each row in a loop
        row_index = 0
        for fileEntry in tqdm(files, desc="Annotations view creation"):
            annotations: list[Annote] = fileEntry["Annotations"]
            visuals: Visuals = fileEntry["Visuals"]

            for index, annotation in enumerate(annotations):

                # Start from column zero
                colIndex = 0

                # Column : Filename + Image
                item = QTableWidgetItem(f"{fileEntry['Name']}_{index}")
                ViewAnnotations.set_cropped_image_tooltip(
                    item,
                    fileEntry["Path"],
                    annotation.xyxy_px(visuals.width, visuals.height),
                )
                item.setData(QtCore.Qt.UserRole, fileEntry["ID"])
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

                # Column : Evaluation
                item = EvaluationTableWidgetItem(annotation.evalution)
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
