"""
Test file for the boxes module.
"""

import pytest

from helpers.gpu import CudaDeviceLowestMemory, IsCuda


def test_lowest_gpu():
    """Test the tiles_iou function."""
    if not IsCuda():
        return

    gpu_id = CudaDeviceLowestMemory()
    assert gpu_id is not None


if __name__ == "__main__":
    test_lowest_gpu()
