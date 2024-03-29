import logging
import os

from Detectors.DetectorYOLOv4 import DetectorYOLOv4
from helpers.files import FixPath, GetFilename, GetFiles


def IsDarknet():
    """Checks if darknet exists cuda is installed and working."""
    if os.system("ls /usr/local/lib/libdarknet.so") == 0:
        return True

    return False


def IsCuda():
    """Checks if GPU cuda is installed and working."""
    if os.system("nvcc --version") == 0:
        return True

    return False


def ListDetectors(path: str = None):
    """List detectors in directory."""
    detectors = []

    # Handle path
    if path is None:
        path = "Detectors/"
    else:
        path = f"{path}/Detectors/"

    for filename in os.listdir(path):
        filepath = path + filename
        # Get directories
        if os.path.isdir(filepath):
            filepath = FixPath(filepath)
            # Get cfg files
            files = GetFiles(filepath, "*.cfg")
            # If any file found
            if len(files) != 0:
                outpath = filepath + GetFilename(files[0])
                logging.info("(Found detector) %u - %s.", len(detectors), outpath)
                detectors.append(
                    (outpath + ".cfg", outpath + ".weights", outpath + ".data")
                )

    return detectors


def CreateDetector(detectorID=0, gpuID=0, path=None):
    """Creates detector."""
    detectors = ListDetectors(path)
    # Create detector
    if detectorID < len(detectors):
        cfgPath, weightPath, metaPath = detectors[detectorID]
        return DetectorYOLOv4(cfgPath, weightPath, metaPath)

    return None


def GetDetectorLabels(detectorID=0):
    """Creates detector."""
    detectors = ListDetectors()
    # Create detector
    if detectorID < len(detectors):
        cfgPath, weightPath, metaPath = detectors[detectorID]
        with open(GetFilename(metaPath) + ".names", "r") as f:
            data = f.readlines()
            return [line.strip() for line in data]

    return []

    return None
