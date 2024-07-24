"""
 Unix os.stat view table widget item.
"""

from PyQt5 import QtCore, QtWidgets
import datetime


class StatTableWidgetItem(QtWidgets.QTableWidgetItem):
    # Float value
    timestamp: float = 0

    def __init__(self, stat_timestamp: float) -> None:
        """Constructor."""
        super().__init__()
        # Set variables
        self.timestamp = stat_timestamp
        self.setData(QtCore.Qt.UserRole, self.timestamp)

        # Text : Format to python datetime and then as string
        dt = datetime.datetime.fromtimestamp(stat_timestamp)
        self.setText(dt.strftime("%Y-%m-%d\n%H:%M:%S"))
        self.setTextAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)

    def __lt__(self, other: QtWidgets.QTableWidgetItem):
        """Operation < for sorting."""
        timestamp = other.data(QtCore.Qt.UserRole)
        return (timestamp is not None) and (self.timestamp < timestamp)
