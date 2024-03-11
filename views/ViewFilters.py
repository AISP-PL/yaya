"""
    View of images QTableWidget.
"""

from PyQt5 import QtCore
from PyQt5.Qt import QSizePolicy, QSpacerItem
from PyQt5.QtWidgets import (
    QButtonGroup,
    QGridLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QWidget,
)
from tqdm import tqdm

from helpers.texts import abbrev
from views.ViewImagesTableRow import ViewImagesTableRow


class ViewFilters:
    """View of filters QTableWidget."""

    # Filter classes group : Static handle
    filter_classes_group: QButtonGroup = None

    @staticmethod
    def ViewClasses(
        layoutHandle: QGridLayout,
        button_ids: list[str],
        button_labels: list[str],
        rowStart: int = 0,
        itemsPerRow: int = 6,
        default_checked: bool = True,
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

        # ButtonGroup : Create group with multiple selection
        ViewFilters.filter_classes_group = QButtonGroup()
        ViewFilters.filter_classes_group.setExclusive(False)

        # Buttons : Create
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
            ViewFilters.filter_classes_group.addButton(button)

            # Button : Set default checked
            button.setChecked(default_checked)

            # # Button : Clicked callback
            # button.clicked.connect(
            #     lambda clicked, paint_name=button_id, paint_group_name=rowName, paint_group_label=qlabel: ViewErrataPaint.PaintSelected(
            #         editor, editor_mode, paint_name, paint_group_name, paint_group_label
            #     )
            # )

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
