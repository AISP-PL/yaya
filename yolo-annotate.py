#!/usr/bin/python3
import argparse
import logging
import os
import sys

import engine.annote as annote
from Detectors import CreateDetector, GetDetectorLabels, IsDarknet
from engine.annoter import Annoter
from helpers.files import FixPath, GetFileLocation
from MainWindow import MainWindowGui


def main():
    """Main code method."""
    # Arguments and config
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        "--input",
        type=str,
        required=True,
        help="Input path",
    )
    parser.add_argument("-c", "--config", type=str, required=False, help="Config path")
    parser.add_argument(
        "-detc",
        "--detectorConfidence",
        type=float,
        nargs="?",
        const=0.4,
        default=0.4,
        required=False,
        help="Detector default confidence",
    )
    parser.add_argument(
        "-detnms",
        "--detectorNms",
        type=float,
        nargs="?",
        const=0.45,
        default=0.45,
        required=False,
        help="Detector default NMS threshold",
    )
    parser.add_argument(
        "-dc",
        "--drawConfidence",
        type=int,
        nargs="?",
        const=1,
        default=1,
        required=False,
        help="Draw annotations confidence (=1). No drawing (=0).",
    )
    parser.add_argument(
        "-sb",
        "--sortBy",
        type=int,
        nargs="?",
        const=2,
        default=2,
        required=False,
        help="Sort by method number (0 None, 1 Datetime, 2 Inv. Datetime, 3 Alphabet)",
    )
    parser.add_argument(
        "-oc",
        "--onlyClass",
        type=int,
        required=False,
        help="Only specific class number",
    )
    parser.add_argument(
        "-odc",
        "--onlyDetectedClass",
        type=int,
        required=False,
        help="Only specific detected class number(Procces all detections)",
    )
    parser.add_argument(
        "-on",
        "--onlyNewFiles",
        action="store_true",
        required=False,
        help="Process only files without detections file.",
    )
    parser.add_argument(
        "-oo",
        "--onlyOldFiles",
        action="store_true",
        required=False,
        help="Process only files with detections file.",
    )
    parser.add_argument(
        "-nd",
        "--noDetector",
        action="store_true",
        required=False,
        help="Disable detector pre processing of files.",
    )
    parser.add_argument(
        "-oe",
        "--onlyFilesWithErrors",
        action="store_true",
        required=False,
        help="Process only files with errors.",
    )
    parser.add_argument(
        "-d",
        "--detector",
        type=int,
        nargs="?",
        const=0,
        default=0,
        required=False,
        help="Detector type - default 0",
    )
    parser.add_argument(
        "-f",
        "--forceDetector",
        action="store_true",
        required=False,
        help="Force detector for every file.",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        required=False,
        help="Show verbose finded and processed data",
    )
    args = parser.parse_args()

    # Check - input argument
    if args.input is None:
        print("Error! No arguments!")
        sys.exit(-1)

    # Check - files filter
    isOnlyNewFiles = False
    if args.onlyNewFiles:
        isOnlyNewFiles = True

    # Check - files filter
    isOnlyOldFiles = False
    if args.onlyOldFiles:
        isOnlyOldFiles = True

    # Check - files filter
    isOnlyErrorFiles = False
    if args.onlyFilesWithErrors:
        isOnlyErrorFiles = True

    # Check - files filter
    isOnlySpecificClass = None
    if args.onlyClass is not None:
        isOnlySpecificClass = args.onlyClass

    # Check - files filter
    isOnlyDetectedClass = None
    if args.onlyDetectedClass is not None:
        isOnlyDetectedClass = args.onlyDetectedClass

    # Check - detector
    noDetector = False
    if args.noDetector is not None:
        noDetector = args.noDetector

    # Check - detector
    forceDetector = False
    if args.forceDetector is not None:
        forceDetector = args.forceDetector

    # Enabled logging
    if __debug__ is True:
        logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    else:
        logging.basicConfig(stream=sys.stderr, level=logging.INFO)
    logging.debug("Logging enabled!")

    # Create detector

    scriptPath = os.path.dirname(os.path.realpath(__file__))
    detector = None
    if IsDarknet() and (noDetector is False):
        detector = CreateDetector(args.detector, path=scriptPath)
        if detector is None:
            logging.error("Wrong detector!")
            return

        detector.Init()
        annote.Init(detector.GetClassNames())
    # CUDA not installed
    else:
        noDetector = True
        annote.Init(GetDetectorLabels(args.detector))

    # Check - input argument
    if (args.input is not None) and (len(args.input) > 0):
        args.input = FixPath(GetFileLocation(args.input))

    # Create annoter
    annoter = Annoter(
        None,
        detector,
        noDetector,
        args.sortBy,
        isOnlyNewFiles,
        isOnlyOldFiles,
        isOnlyErrorFiles,
        isOnlyDetectedClass,
        isOnlySpecificClass,
        forceDetector,
        detectorConfidence=args.detectorConfidence,
        detectorNms=args.detectorNms,
    )

    # Start QtGui
    gui = MainWindowGui(args, detector, annoter)
    sys.exit(gui.Run())


if __name__ == "__main__":
    main()
