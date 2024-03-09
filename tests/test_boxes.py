"""
Test file for the boxes module.
"""

import pytest

from helpers.boxes import tiles_iou


def test_tiles_iou():
    """Test the tiles_iou function."""
    # Same tiles
    box1 = (0, 0, 100, 100)
    assert tiles_iou(box1, box1) == 0

    # Neighbouring tiles right-left
    box1 = (0, 0, 100, 100)
    box2 = (100, 0, 200, 100)
    assert tiles_iou(box1, box2) == 1
    assert tiles_iou(box2, box1) == 1

    # Neighbouring tiles top-bottom
    box1 = (0, 0, 100, 100)
    box2 = (0, 100, 100, 200)
    assert tiles_iou(box1, box2) == 1
    assert tiles_iou(box2, box1) == 1

    # Neighbouring tiles left, big and small
    box1 = (0, 0, 100, 100)
    box2 = (100, 0, 150, 50)
    assert tiles_iou(box1, box2) >= 0.8

    # Separate tiles (same size)
    box1 = (0, 0, 1, 1)
    box2 = (2, 2, 3, 3)
    assert tiles_iou(box1, box2) > 0.2

    # Separate tiles (big and small)
    box1 = (0, 0, 1, 1)
    box2 = (2, 2, 10, 10)
    assert tiles_iou(box1, box2) >= 0.65


def test_tiles_sim():
    """Test"""


if __name__ == "__main__":
    test_tiles_iou()
