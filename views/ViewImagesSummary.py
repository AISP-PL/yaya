'''
    View of images QTableWidget.
'''
from dataclasses import dataclass, field
from PyQt5.QtWidgets import QLabel
from PyQt5 import QtCore


@dataclass
class Summary:
    ''' Summary of image file entries.'''
    _files: int = field(init=False, default=0)
    _correct: float = field(init=True, default=0)
    _correct_bboxes: float = field(init=True, default=0)
    new_detections: int = field(init=True, default=0)
    _precision: float = field(init=True, default=0)
    _recall: float = field(init=True, default=0)

    @property
    def correct(self) -> float:
        ''' Returns % of correct detections.'''
        if (self._files == 0):
            return 0

        return self._correct / self._files

    @property
    def correct_bboxes(self) -> float:
        ''' Returns % of correct detections.'''
        if (self._files == 0):
            return 0

        return self._correct_bboxes / self._files

    @property
    def precision(self) -> float:
        ''' Returns metric.'''
        if (self._files == 0):
            return 0

        return self._precision / self._files

    @property
    def recall(self) -> float:
        ''' Returns metric.'''
        if (self._files == 0):
            return 0

        return self._recall / self._files

    def Add(self, fileEntry: dict) -> None:
        ''' Add fileEntry to summary'''
        # Check : Invalid fileEntry
        if (fileEntry is None):
            return

        # Get metrics
        metrics = fileEntry['Metrics']

        # Add metrics
        self._correct += metrics.correct
        self._correct_bboxes += metrics.correct_bboxes
        self.new_detections += metrics.new_detections
        self._precision += metrics.precision
        self._recall += metrics.recall

        # Files : count
        self._files += 1


class ViewImagesSummary:

    @staticmethod
    def View(label: QLabel, files: list):
        ''' View images in table.'''
        # Check : Invalid files list
        if (files is None) or (len(files) == 0):
            return

        # Get translations
        _translate = QtCore.QCoreApplication.translate

        # Files summary create
        summary = Summary()
        for fileEntry in files:
            summary.Add(fileEntry)

        # View files summary.
        text = ''
        text += f'Avg correctness is **{summary.correct:2.2f}%** (only boxes {summary.correct_bboxes:2.2f}%).\n'
        text += f'New detections: **{summary.new_detections}**.\n\n'
        text += f'Avg Precision: {summary.precision:.2f}. Avg Recall: {summary.recall:.2f}\n'

        # Update label object
        label.setText(text)
