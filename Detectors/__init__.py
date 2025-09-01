import logging
import os
from enum import Enum
from typing import Optional

from helpers.files import FixPath, GetFilename, GetFiles


class DetectorType(str, Enum):
    """Different detector types."""

    Darknet = "Darknet"
    CVDNN = "CVDNN"
    Ultralytics = "YOLOv8"


def IsDarknet() -> bool:
    """Checks if darknet exists cuda is installed and working."""
    if os.path.exists("/usr/local/lib/libdarknet.so"):
        return True

    return False


def ListDetectors(path: Optional[str] = None) -> list[tuple[str, str, str]]:
    """List detectors in directory."""

    # List of detectors
    detectors: list[tuple, tuple, tuple] = []

    # Handle path
    if path is None:
        path = "Detectors/"
    else:
        path = f"{path}/Detectors/"

    for filename in os.listdir(path):
        subpath = path + filename
        # Check : Not a directory, skip
        if not os.path.isdir(subpath):
            continue

        subpath = FixPath(subpath)
        # Get cfg files
        cfg_files = GetFiles(subpath, "*.cfg")

        # Check : If CFG files found
        if len(cfg_files) != 0:
            # Darknet detector : Add
            outpath = subpath + GetFilename(cfg_files[0])
            logging.info("(Found detector) %u - %s.", len(detectors), outpath)
            detectors.append(
                (
                    DetectorType.Darknet,
                    outpath + ".cfg",
                    outpath + ".weights",
                    outpath + ".data",
                    outpath + ".names",
                )
            )

        # Find *.pt files as YOLOv5/YOLOv8 detectors
        pt_files = GetFiles(subpath, "*.pt")

        # Ultralytics detector : Add if found
        if len(pt_files) != 0:
            first_file = pt_files[0]
            subpath = FixPath(path + first_file)
            outpath = subpath[: subpath.rfind(".")]
            logging.info("(Found detector) %u - %s.", len(detectors), outpath)
            detectors.append(
                (
                    DetectorType.Ultralytics,
                    "",  # No cfg file
                    outpath + ".pt",
                    "",  # No meta file
                    outpath + ".names",
                )
            )

    return detectors


def CreateDetector(detectorID: int = 0, gpuID: int = 0, path: str = None):
    """Creates detector."""
    detectors = ListDetectors(path)
    if detectorID >= len(detectors):
        return None

    # Detector type : Get
    detector_type, cfgPath, weightPath, metaPath, namesPath = detectors[detectorID]

    # Ultralytics : Creation
    if detector_type == DetectorType.Ultralytics:
        from Detectors.detector_yolov8_ultralytics import DetectorYolov8

        return DetectorYolov8(
            weights_path=weightPath, names_path=namesPath, gpu_id=gpuID
        )

    # Darknet : Creation
    if IsDarknet():
        from Detectors.DetectorYOLOv4 import DetectorYOLOv4

        try:
            detector = DetectorYOLOv4(cfgPath, weightPath, metaPath)
            return detector
        except Exception as e:
            logging.error("Darknet loading error! Fallback to CVDNN. %s", e)

    # CVDNN : Creation
    from Detectors.detector_yolov4_cvdnn import DetectorCVDNN

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
