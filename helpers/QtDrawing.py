"""
Created on 30 gru 2020

@author: spasz
"""

from enum import Enum, auto
from random import randint

import numpy as np
from PyQt5.Qt import QFontMetrics, QPoint
from PyQt5.QtCore import QRect, Qt
from PyQt5.QtGui import QBrush, QColor, QImage, QPen, QPixmap, QPolygon, QTransform
from PyQt5.QtWidgets import QTableWidgetItem

import Gui.colors as colors
import helpers.algebra as algebra


class TextAlignment(str, Enum):
    """Text alignment enum."""

    Center = auto()
    TopRight = auto()
    TopLeft = auto()
    BottomRight = auto()
    BottomLeft = auto()


def CvBGRColorToQColor(color: tuple) -> QColor:
    """Translate bgr OpenCV color to QColor."""
    return QColor(color[2], color[1], color[0])


def CvRGBColorToQColor(color):
    """Translate bgr OpenCV color to QColor."""
    return QColor(color[0], color[1], color[2])


def CvColorToQBrush(color):
    """Translate bgr OpenCV color to QColor."""
    return QBrush(QColor(color[2], color[1], color[0]))


def GetRandomQColor():
    """Returns random QColor."""
    return QColor(randint(0, 255), randint(0, 255), randint(0, 255))


def QPointToTuple(point):
    """Return tuple instead of QPoint."""
    return (point.x(), point.y())


def QPointListToTupleList(pointslist):
    """Return tuple list instead of QPoint list."""
    return [(point.x(), point.y()) for point in pointslist]


def TupleListToQPoints(pointslist):
    """Return tuple list instead of QPoint list."""
    return [QPoint(x, y) for x, y in pointslist]


def CvImage2QtImage(cvImg):
    """Convert CV image to QPixmap."""
    return QPixmap(
        QImage(
            np.require(cvImg, np.uint8, "C"),
            cvImg.shape[1],
            cvImg.shape[0],
            cvImg.shape[1] * 3,
            QImage.Format_RGB888,
        ).rgbSwapped()
    )


def CreateBoolColorQTableWidgetItem(result):
    """Creates colored QTableWidgetitem."""
    item = QTableWidgetItem(str(result))
    if result is True:
        item.setBackground(CvColorToQBrush(colors.green))
    else:
        item.setBackground(CvColorToQBrush(colors.red))
    return item


def QTableWidgetItemSetBoolColor(item, result):
    """Creates colored QTableWidgetitem."""
    if result is True:
        item.setBackground(CvColorToQBrush(colors.green))
    else:
        item.setBackground(CvColorToQBrush(colors.red))
    return item


def CreateTraingle(x, y, size=10, angle=0) -> QPolygon:
    """
        Creates polygon as triangle, at given position(x,y)
        Traingle is directed along x axis -->.
        |\
        | >
        |/
    ."""
    # Create right pointing triangle as polygon
    width = size
    height = int(size * 0.5)
    polygon = QPolygon()
    polygon.append(QPoint(width, 0))  # peak
    polygon.append(QPoint(0, height))  # top
    polygon.append(QPoint(0, -height))  # bottom
    # Rotate by angle
    if angle != 0:
        transform = QTransform()
        transform.rotate(angle)
        polygon = transform.map(polygon)
    # Move to point (x,y)
    polygon.translate(x, y)

    return polygon


def CreateRectangle(
    x, y, width=100, height=20, align: TextAlignment = TextAlignment.Center
) -> QRect:
    """
        Creates polygon as rectangle centered
        in the center of axes.
    ."""
    rect = QRect(x, y, width, height)

    # Alignment
    # Info : Y axis is inverted on screen.
    # top left    | top right
    # ------------+-----------
    # bottom left | bottom right
    if align == TextAlignment.Center:
        rect.translate(round(-width / 2), round(-height / 2))
    if align == TextAlignment.TopRight:
        rect.translate(0, -height)
    elif align == TextAlignment.TopLeft:
        rect.translate(-width, -height)
    elif align == TextAlignment.BottomRight:
        """Default, do nothing."""
    elif align == TextAlignment.BottomLeft:
        rect.translate(-width, 0)

    return rect


def QDrawTriangle(
    painter,
    point,
    size=10,
    angle=0,
    pen=Qt.black,
    brushColor=Qt.white,
    brushStyle=Qt.SolidPattern,
    brushOpacity=1,
):
    """Helper function for polygon drawing."""
    polygon = CreateTraingle(point.x(), point.y(), size, angle)
    # Set pen and brush
    painter.setPen(pen)
    color = QColor(brushColor)
    color.setAlphaF(brushOpacity)
    painter.setBrush(QBrush(color, brushStyle))
    # Draw
    painter.drawPolygon(polygon)


def QDrawRectangleWH(
    painter,
    point,
    width=100,
    height=20,
    angle=0,
    pen=Qt.black,
    brushColor=Qt.white,
    brushStyle=Qt.SolidPattern,
    brushOpacity=1,
):
    """Helper function for polygon drawing."""
    polygon = CreateRectangle(point.x(), point.y(), width, height, angle)
    # Set pen and brush
    painter.setPen(pen)
    color = QColor(brushColor)
    color.setAlphaF(brushOpacity)
    painter.setBrush(QBrush(color, brushStyle))
    # Draw
    painter.drawPolygon(polygon)


def QDrawRectangle(
    painter,
    points,
    pen=Qt.black,
    penThickness=1,
    penStyle=Qt.SolidLine,
    brushColor=Qt.white,
    brushStyle=Qt.SolidPattern,
    brushOpacity=1,
) -> None:
    """Helper function for polygon drawing."""
    p1 = points[0]
    p2 = points[1]
    # Create polygon zero-shot from points list
    polygon = QPolygon(
        [
            QPoint(int(p2.x()), int(p1.y())),
            QPoint(int(p1.x()), int(p1.y())),
            QPoint(int(p1.x()), int(p2.y())),
            QPoint(int(p2.x()), int(p2.y())),
        ]
    )

    # Set pen and brush
    painter.setPen(QPen(pen, penThickness, penStyle))
    color = QColor(brushColor)
    color.setAlphaF(brushOpacity)
    painter.setBrush(QBrush(color, brushStyle))

    # Draw
    painter.drawPolygon(polygon)


def QDrawText(
    painter,
    point,
    text,
    fontSize=10,
    fontBold=False,
    pen=Qt.white,
    bgColor=Qt.black,
    bgStyle=Qt.SolidPattern,
    bgOpacity=1,
    bgMargin=2,
    textAlign: TextAlignment = TextAlignment.Center,
):
    """Helper function for polygon drawing."""
    # Font : create & set
    font = painter.font()
    font.setPixelSize(fontSize)
    font.setBold(fontBold)
    font.setFamily("Arial")
    painter.setFont(font)

    # Get font height.
    metric = QFontMetrics(font)
    # Get number of font text lines.
    textLines = text.split("\n")
    # Get max width/height
    textHeight = metric.height()
    textWidth = max([metric.width(text) for text in textLines])
    # BgRect : Width and Height
    bgRectWidth = textWidth + bgMargin * 2
    bgRectHeight = textHeight * len(textLines) + bgMargin * 2

    # Creat 4-point rectangle.
    bgrect = CreateRectangle(
        point.x(), point.y(), bgRectWidth, bgRectHeight, align=textAlign
    )

    # Pen set
    painter.setPen(pen)

    # Draw background if enabled
    if bgColor is not None:
        painter.fillRect(bgrect, bgColor)

    # TextPoint : TopLeft + margin + textHeight
    textPoint = bgrect.topLeft() + QPoint(bgMargin, textHeight)

    # Draw text
    for text in textLines:
        painter.drawText(textPoint, text)
        textPoint += QPoint(0, textHeight)

    # Return end point of text rect.
    return (bgrect.bottomRight().x(), bgrect.bottomRight().y())


def QDrawCrosshair(
    painter,
    x: float,
    y: float,
    width: int,
    height: int,
    penColor=Qt.black,
    penColorAlpha: float = 1.0,
    penThickness: int = 1,
    penStyle=Qt.SolidLine,
    length: int = 50,
):
    """Helper function for polyline drawing."""
    # Set Pen
    color = QColor(penColor)
    color.setAlphaF(penColorAlpha)
    pen = QPen(color, penThickness, penStyle)
    painter.setPen(pen)

    # Draw
    painter.drawLine(int(x), int(y - length), int(x), int(y + length))
    painter.drawLine(int(x - length), int(y), int(x + length), int(y))


def QDrawPolygon(
    painter,
    pointsList,
    pen=Qt.black,
    brushColor=Qt.white,
    brushStyle=Qt.CrossPattern,
    brushOpacity=1,
):
    """Helper function for polygon drawing."""
    polygon = QPolygon()
    for point in pointsList:
        polygon.append(point)
    painter.setPen(pen)
    color = QColor(brushColor)
    color.setAlphaF(brushOpacity)
    painter.setBrush(QBrush(color, brushStyle))
    painter.drawPolygon(polygon)


def QDrawPolyline(
    painter,
    pointsList,
    penColor=Qt.black,
    penColorAlpha=1.0,
    penThickness=1,
    penStyle=Qt.SolidLine,
    isClosed=False,
):
    """Helper function for polyline drawing."""
    polygon = QPolygon()
    for point in pointsList:
        polygon.append(point)
    if isClosed:
        polygon.append(pointsList[0])
    color = QColor(penColor)
    color.setAlphaF(penColorAlpha)
    pen = QPen(color, penThickness, penStyle)
    painter.setPen(pen)
    painter.drawPolyline(polygon)


def QDrawArrow(
    painter,
    pointsList,
    penColor=Qt.black,
    penColorAlpha=1.0,
    penThickness=1,
    penStyle=Qt.SolidLine,
):
    """Helper function for polyline drawing."""
    # Set pen
    color = QColor(penColor)
    color.setAlphaF(penColorAlpha)
    pen = QPen(color, penThickness, penStyle)
    painter.setPen(pen)
    # Create polygon and draw arrow
    polygon = QPolygon()
    for point in pointsList:
        polygon.append(point)
    painter.drawPolyline(polygon)
    # Calculate arrow angle
    tupleList = QPointListToTupleList(pointsList)
    angle = algebra.GetTuplePointsAngle(tupleList[-2], tupleList[-1])
    QDrawTriangle(painter, pointsList[-1], size=15, angle=angle, pen=penColor)


def QDrawDistances(
    painter,
    distance,
    penColor=Qt.black,
    penColorAlpha=1.0,
    penThickness=1,
    penStyle=Qt.SolidLine,
):
    """Helper function for polyline drawing."""
    pointsList = distance["QViewTrajectory"]
    # Draw joints
    QDrawJoints(painter, pointsList, 5, Qt.black, penColor, Qt.SolidPattern, 0.5)
    # Draw line 1
    QDrawPolyline(
        painter, pointsList[0:2], penColor, penColorAlpha, penThickness, penStyle
    )
    # Draw line 2
    QDrawPolyline(
        painter, pointsList[2:4], penColor, penColorAlpha, penThickness, penStyle
    )
    # Calculate center line
    tupleList = QPointListToTupleList(pointsList)
    pc0 = algebra.GetMiddlePoint(tupleList[0], tupleList[1])
    pc1 = algebra.GetMiddlePoint(tupleList[2], tupleList[3])
    QDrawPolyline(
        painter,
        [QPoint(pc0[0], pc0[1]), QPoint(pc1[0], pc1[1])],
        penColor,
        penColorAlpha,
        penThickness,
        penStyle,
    )
    # Draw letter at the begining
    QDrawText(
        painter,
        QPoint(pc0[0], pc0[1]),
        "%s %2.2fm" % (distance["id"], distance["distance"]),
        fontSize=20,
        fontBold=True,
    )


def QDrawElipse(
    painter,
    point,
    radius=10,
    pen=Qt.black,
    brushColor=Qt.white,
    brushStyle=Qt.CrossPattern,
    brushOpacity=1,
):
    """Helper function for polyline drawing."""
    painter.setPen(pen)
    color = QColor(brushColor)
    color.setAlphaF(brushOpacity)
    painter.setBrush(QBrush(color, brushStyle))
    painter.drawEllipse(point, radius, radius)


def QDrawJoints(
    painter,
    pointsList,
    radius=10,
    pen=Qt.black,
    brushColor=Qt.white,
    brushStyle=Qt.CrossPattern,
    brushOpacity=1,
):
    """Helper function for polyline drawing."""
    painter.setPen(pen)
    color = QColor(brushColor)
    color.setAlphaF(brushOpacity)
    painter.setBrush(QBrush(color, brushStyle))
    for point in pointsList:
        painter.drawEllipse(point, radius, radius)
