"""
    View of images QTableWidget.
"""

from typing import Callable

from PyQt5 import QtCore
from PyQt5.Qt import QSizePolicy, QSpacerItem
from PyQt5.QtWidgets import QButtonGroup, QGridLayout, QLabel, QPushButton

from helpers.texts import abbrev


class ViewFilters:
    """View of filters QTableWidget."""

    # Filter images group : Static handle
    filter_images_group: QButtonGroup = QButtonGroup()
    # Filter classes group : Static handle
    filter_classes_group: QButtonGroup = QButtonGroup()
    # Filter detections group : Static handle
    filter_detections_group: QButtonGroup = QButtonGroup()

    @staticmethod
    def ViewClasses(
        layoutHandle: QGridLayout,
        layout_title: str,
        button_ids: list[str],
        button_labels: list[str],
        button_callback: callable,
        buttons_group: QButtonGroup,
        rowStart: int = 0,
        itemsPerRow: int = 10,
        default_checked: bool = False,
        label_max_length: int = 12,
    ):
        """
        Creates errata paint grid layout.

        Returns : Next row start index.
        """
        # Layout : Clear if exists or force clear
        # Qt : Safe way to clear layout
        while (child := layoutHandle.takeAt(0)) is not None:
            widget = child.widget()
            if widget is not None:
                widget.setParent(None)

            del child

        # Label : Add title
        # layoutHandle.addWidget(QLabel(layout_title), rowStart, 0)
        # rowStart += 1

        # ButtonGroup : Create group with multiple selection
        buttons_group.setExclusive(False)

        # Buttons : Create
        rowIndex: int = rowStart
        for button_index, button_id in enumerate(button_ids):
            # Label : Get
            button_label = abbrev(button_labels[button_index], label_max_length)

            # Button : Create
            button = QPushButton(button_label)
            button.setToolTip(button_id)
            button.setCursor(QtCore.Qt.PointingHandCursor)
            button.setCheckable(True)
            button.setMinimumWidth(96)
            button.setMaximumWidth(128)

            # ButtonGroup : Add button
            buttons_group.addButton(button)

            # Button : Set default checked
            button.setChecked(default_checked)

            # # Button : Clicked callback
            button.clicked.connect(
                lambda clicked, button_id=button_id: button_callback(button_id)
            )

            # Row and column index : Calculate
            rowIndex = rowStart + int(button_index / itemsPerRow)
            colIndex = 1 + button_index % itemsPerRow

            # Insert QButton into grid layout
            layoutHandle.addWidget(button, rowIndex, colIndex)

            # Check : If last button or last button in row, add spacer at the end
            if (((button_index + 1) % itemsPerRow) == 0) or (
                button_index == len(button_ids) - 1
            ):
                layoutHandle.addItem(
                    QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Minimum),
                    rowIndex,
                    colIndex + 1,
                )

        # Return next row start
        return rowIndex + 1

    @staticmethod
    def ViewImages(
        layoutHandle: QGridLayout,
        callback_annotated_only: Callable,
        callback_validation_only: Callable,
    ) -> None:
        """
        Creates errata paint grid layout.
        """
        # Layout : Clear if exists or force clear
        # Qt : Safe way to clear layout
        while (child := layoutHandle.takeAt(0)) is not None:
            widget = child.widget()
            if widget is not None:
                widget.setParent(None)

            del child

        # Button : Filter only annotated
        button = QPushButton("Annotated only")
        button.setToolTip("Annotated only")
        button.setCursor(QtCore.Qt.PointingHandCursor)
        button.setCheckable(True)
        button.setMinimumWidth(96)
        button.setMaximumWidth(128)
        button.clicked.connect(callback_annotated_only)
        layoutHandle.addWidget(button, 0, 0)

        # Button : Filter only validation
        button = QPushButton("Validation only")
        button.setToolTip("Validation only")
        button.setCursor(QtCore.Qt.PointingHandCursor)
        button.setCheckable(True)
        button.setMinimumWidth(96)
        button.setMaximumWidth(128)
        button.clicked.connect(callback_validation_only)
        layoutHandle.addWidget(button, 0, 1)
