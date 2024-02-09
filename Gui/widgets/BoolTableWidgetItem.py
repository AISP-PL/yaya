'''
Created on 14 gru 2022

@author: spasz
'''
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QColor
from PyQt5.QtGui import QBrush, QPolygon, QColor, QPen, QTransform, QPainter


class BoolTableWidgetItem(QtWidgets.QTableWidgetItem):
    # value
    value: bool = False
    # Flag
    isBackgroundForced: bool = False

    def __init__(self,
                 value: bool = False,
                 forceBackground: bool = False,
                 ):
        ''' Constructor.'''
        super().__init__()
        # Set variables
        self.value = value
        self.isBackgroundForced = forceBackground

        # Set item data
        self.setData(QtCore.Qt.UserRole, value)
        self.autosetText()
        self.autosetBackground()

    def autosetText(self):
        ''' Autoset text and tooltip.'''
        # Get translations
        _translate = QtCore.QCoreApplication.translate

        if (self.value is True):
            self.setText(_translate('BoolTableWidgetItem', 'Yes'))
        else:
            self.setText(_translate('BoolTableWidgetItem', 'No'))

        # Text formatting
        self.setTextAlignment(QtCore.Qt.AlignCenter)

    def autosetBackground(self):
        ''' Autoset bg color.'''
        if (self.value is True):
            self.setBackground(QBrush(QColor('#009970')))
        else:
            self.setBackground(QBrush(QColor('#990000')))

    def setBackground(self, color: QColor):
        ''' Allows to set background color.'''
        if (not self.isBackgroundForced):
            QtWidgets.QTableWidgetItem.setBackground(self, color)
        else:
            self.autosetBackground()

    def __lt__(self, other: QtWidgets.QTableWidgetItem):
        ''' Operation < for sorting.'''
        value = other.data(QtCore.Qt.UserRole)
        return (value is not None) and (self.value < value)
