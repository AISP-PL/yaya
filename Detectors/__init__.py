import logging
import os
from typing import Optional

from helpers.files import FixPath, GetFilename, GetFiles


def IsDarknet() -> bool:
    """Checks if darknet exists cuda is installed and working."""
    if os.path.exists("/usr/local/lib/libdarknet.so") == 0:
        return True

    return False


def ListDetectors(path: Optional[str] = None) -> list[tuple[str, str, str]]:
    """List detectors in directory."""
    detectors: list[tuple, tuple, tuple] = []

    # Handle path
    if path is None:
        path = "Detectors/"
    else:
        path = f"{path}/Detectors/"

    for filename in os.listdir(path):
        filepath = path + filename
        # Check : Not a directory, skip
        if not os.path.isdir(filepath):
            continue

        filepath = FixPath(filepath)
        # Get cfg files
        files = GetFiles(filepath, "*.cfg")

        # Check : If no cfg file found
        if len(files) == 0:
            continue

        outpath = filepath + GetFilename(files[0])
        logging.info("(Found detector) %u - %s.", len(detectors), outpath)
        detectors.append(
            (
                outpath + ".cfg",
                outpath + ".weights",
                outpath + ".data",
                outpath + ".names",
            )
        )

    return detectors


def CreateDetector(detectorID: int = 0, gpuID: int = 0, path: str = None):
    """Creates detector."""
    detectors = ListDetectors(path)
    if detectorID >= len(detectors):
        return None

    # Darknet : Creation
    if IsDarknet():
        from Detectors.DetectorYOLOv4 import DetectorYOLOv4

        try:
            cfgPath, weightPath, metaPath, namesPath = detectors[detectorID]
            detector = DetectorYOLOv4(cfgPath, weightPath, metaPath)
            return detector
        except Exception as e:
            logging.error("Darknet loading error! Fallback to CVDNN. %s", e)

    # CVDNN : Creation
    from Detectors.detector_yolov4_cvdnn import DetectorCVDNN

    cfgPath, weightPath, metaPath, namesPath = detectors[detectorID]
    return DetectorCVDNN(cfgPath, weightPath, metaPath, namesPath)


def GetDetectorLabels(detectorID=0):
    """Creates detector."""
    detectors = ListDetectors()
    # Create detector
    if detectorID < len(detectors):
        cfgPath, weightPath, metaPath, namespath = detectors[detectorID]
        with open(namespath, "r") as f:
            data = f.readlines()
            return [line.strip() for line in data]

    return []
