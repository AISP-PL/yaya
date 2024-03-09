"""
 Boxes helper module

Created on 21 lip 2020
@author: spasz
"""

import math

from helpers import algebra


class BoxState:
    """
    Box occlusion/conatining state.
    """

    Isolated = 0
    Occluding = 0x01
    Occluded = 0x02
    Containing = 0x04
    Contained = 0x08

    def __init__(self):
        """constructor"""
        self.state = self.Isolated

    def Reset(self):
        """Resets my state"""
        self.state = self.Isolated

    def Set(self, state):
        """Overrides state with higher priority state."""
        self.state |= state

    def Get(self):
        """Returns tracker state"""
        return self.state

    def IsSet(self, bit):
        """Is state bit set"""
        return (self.state & bit) == bit

    def toSymbol(self):
        """State symbols array"""
        symbols = ["O", "o", "C", "c"]
        symbol = ""
        for i in range(len(symbols)):
            bit = 1 << i
            if self.state & bit:
                symbol += symbols[i]
        return symbol


def Bbox2Rect(bbox):
    """
    From bounding box yolo format
    to corner points cv2 rectangle
    """
    x, y, w, h = bbox
    xmin = x - (w / 2)
    xmax = x + (w / 2)
    ymin = y - (h / 2)
    ymax = y + (h / 2)
    return xmin, ymin, xmax, ymax


def Rect2Bbox(rect):
    """
    From bounding box yolo format
    to corner points cv2 rectangle
    """
    x, y = GetCenter(rect)
    w = GetWidth(rect)
    h = GetHeight(rect)
    return x, y, w, h


def PointsToRect(p1, p2):
    """Create proper rect from 2 points."""
    x1, y1 = p1
    x2, y2 = p2
    return min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2)


def GetCenter(box):
    """Get center of tracker pos"""
    x, y, x2, y2 = box
    return ((x + x2) / 2), ((y + y2) / 2)


def GetTopCenter(box, height=0):
    """Get center of tracker pos"""
    x, y, x2, y2 = box
    return int((x + x2) / 2), int(max(y, y2) - abs(y - y2) * height)


def GetBottomCenter(box, height=0):
    """Get center of tracker pos"""
    x, y, x2, y2 = box
    return int((x + x2) / 2), int(min(y, y2) + abs(y - y2) * height)


def GetDiagonal(box):
    """Get diagonal of tracker pos"""
    x, y, x2, y2 = box
    return int(math.sqrt((x - x2) * (x - x2) + (y - y2) * (y - y2)))


def GetWidth(box):
    """Get W of box"""
    return abs(box[2] - box[0])


def GetHeight(box):
    """Get H of box"""
    x, y, x2, y2 = box
    return abs(box[3] - box[1])


def FlipHorizontally(width, box):
    """Flip horizontally box."""
    x, y, x2, y2 = box
    return width - x, y, width - x2, y2


def GetArea(box):
    """Get Area of box"""
    x, y, x2, y2 = box
    return abs((x2 - x) * (y2 - y))


def GetDistance(box1, box2):
    """Get distance between two boxes"""
    # Get center as float
    x1, y1, x2, y2 = box1
    p1 = ((x1 + x2) / 2, (y1 + y2) / 2)
    # Get center as float
    x1, y1, x2, y2 = box2
    p2 = ((x1 + x2) / 2, (y1 + y2) / 2)
    return algebra.EuclideanDistance(p1, p2)


def GetCommonsection(x1, x1e, x2, x2e):
    """Returns common section  of cooridantes"""
    begin = max(min(x1, x1e), min(x2, x2e))
    end = min(max(x1, x1e), max(x2, x2e))
    if begin < end:
        return begin, end
    return 0, 0


def GetCommonsectionLength(x1, x1e, x2, x2e):
    """Returns common section  of cooridantes"""
    begin, end = GetCommonsection(x1, x1e, x2, x2e)
    return end - begin


def GetIntersectionArea(box1, box2):
    """Returns area of intersection box"""
    x1, y1, x1e, y1e = box1
    x2, y2, x2e, y2e = box2
    width = GetCommonsectionLength(x1, x1e, x2, x2e)
    height = GetCommonsectionLength(y1, y1e, y2, y2e)
    return width * height


def GetContainingBox(box1: tuple, box2: tuple) -> tuple:
    """Get box containing box1 and box2."""
    x1, y1, x2, y2 = box1
    x3, y3, x4, y4 = box2
    # left top corner
    xl = min(x1, x2, x3, x4)
    yl = min(y1, y2, y3, y4)
    # right bottom corner
    xr = max(x1, x2, x3, x4)
    yr = max(y1, y2, y3, y4)
    # result
    return (xl, yl, xr, yr)


def ToRelative(box, width, height):
    """Rescale all coordinates to relative."""
    x1, y1, x2, y2 = box
    x1 = x1 / width
    x2 = x2 / width
    y1 = y1 / height
    y2 = y2 / height
    return (x1, y1, x2, y2)


def ToAbsolute(box, width, height):
    """Rescale all coordinates to relative."""
    x1, y1, x2, y2 = box
    x1 = int(x1 * width)
    x2 = int(x2 * width)
    y1 = int(y1 * height)
    y2 = int(y2 * height)
    return (x1, y1, x2, y2)


def ToPolygon(box):
    """Transfer bbox to polygon vector."""
    x, y, x2, y2 = box
    return [(x, y), (x2, y), (x2, y2), (x, y2)]


def PointToAbsolute(point, width, height):
    """Rescale all coordinates to absolute."""
    x1, y1 = point
    x1 = x1 * width
    y1 = y1 * height
    return x1, y1


def PointToRelative(point, width, height):
    """Rescale all coordinates to relative."""
    x1, y1 = point
    x1 = x1 / width
    y1 = y1 / height
    return x1, y1


def IsInside(point, box):
    """Return true if point is inside a box."""
    x, y = point
    x1, y1, x2, y2 = box
    return ((x >= x1) and (x <= x2)) and ((y >= y1) and (y <= y2))


def IsContaining(box1, box2):
    """Is occlusion happens then returns which box is occluding"""
    area1 = GetArea(box1)
    area2 = GetArea(box2)
    if GetIntersectionArea(box1, box2) == area1:
        return True, BoxState.Contained, BoxState.Containing
    if GetIntersectionArea(box1, box2) == area2:
        return True, BoxState.Containing, BoxState.Contained
    return False, BoxState.Isolated, BoxState.Isolated


def IsOcclusion(box1, box2):
    """Is occlusion happens then returns which box is occluding"""
    if GetIntersectionArea(box1, box2) != 0:
        area1 = GetArea(box1)
        area2 = GetArea(box2)

        # Assumption : Bigger box is occluding smaller box
        if area1 > area2:
            return True, BoxState.Occluding, BoxState.Occluded
        return True, BoxState.Occluded, BoxState.Occluding
    return False, BoxState.Isolated, BoxState.Isolated


def GetBoxesState(box1, box2):
    """Is occlusion happens then returns which box is occluding"""
    intersection = GetIntersectionArea(box1, box2)
    if intersection != 0:
        area1 = GetArea(box1)
        area2 = GetArea(box2)

        # Contained
        if intersection == area1:
            return BoxState.Contained, BoxState.Containing
        # Containing
        if intersection == area2:
            return BoxState.Containing, BoxState.Contained
        # Occluding
        # Assumption : Bigger box is occluding smaller box
        if area1 > area2:
            return BoxState.Occluding, BoxState.Occluded
        return BoxState.Occluded, BoxState.Occluding
    return BoxState.Isolated, BoxState.Isolated


def ExtractBoxImagePart(im, box):
    """Extract image part where it fits
    box."""
    # Image height and width
    height, width = im.shape[0:2]
    # Unpack detection bbox
    x1, y1, x2, y2 = box
    # Image area assertions
    x1 = min(width, max(0, x1))
    x2 = min(width, max(0, x2))
    y1 = min(height, max(0, y1))
    y2 = min(height, max(0, y2))
    # Extract area
    area = im[y1 : y2 + 1, x1 : x2 + 1]
    return area


def iou(box1: tuple, box2: tuple):
    """Calculates metric."""
    area1 = GetArea(box1)
    area2 = GetArea(box2)
    intersection = GetIntersectionArea(box1, box2)

    # Check : No intersection
    if intersection == 0:
        return 0

    return intersection / (area1 + area2 - intersection)


def tiles_iou(box1: tuple, box2: tuple):
    """
    Metric for calculating possiblity of two
    boxes from two different tiles to be the same box.
    If missing area (difference between containing box and
    two boxes areas) is smaller then value is bigger.

    """
    # Calculate containing box
    cont_box = GetContainingBox(box1, box2)

    # Check : Intersection == 0, -> IOU always zero.
    cont_area = GetArea(cont_box)
    area1 = GetArea(box1)
    area2 = GetArea(box2)
    intersection = GetIntersectionArea(box1, box2)

    # Calculate difference between 2xintersection and containing box
    difference_area = cont_area - (area1 + area2 - 2 * intersection)

    # Normalize
    return 1 - (difference_area / cont_area)
