#!/usr/bin/python3
import argparse
import logging
import os
import sys

from helpers.files import FixPath, IsImageFile
from helpers.textAnnotations import IsExistsAnnotations


def GetAnnotatedImages(path: str):
    """List directory images."""
    # filter only images and not excludes
    excludes = [".", "..", "./", ".directory"]
    filenames = os.listdir(path)

    # Filter images only
    filenames = [f for f in filenames if (f not in excludes) and (IsImageFile(f))]

    # Get only images with annotations
    filenamesAnnotated = [
        f for f in filenames if (IsExistsAnnotations(path + f) == True)
    ]

    return filenamesAnnotated


def main():
    """Main code method."""
    # Enabled logging
    if __debug__ is True:
        logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    else:
        logging.basicConfig(stream=sys.stderr, level=logging.INFO)
    logging.debug("Logging enabled!")

    # Arguments and config
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", type=str, required=True, help="Input path")
    parser.add_argument(
        "-o", "--output", type=str, required=True, help="Output listing file path"
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        required=False,
        help="Show verbose finded and processed data",
    )
    args = parser.parse_args()

    # Input path
    path = FixPath(args.input)

    # Get annotated images
    annotated = GetAnnotatedImages(path)

    # Save results
    with open(args.output, "w") as f:
        for line in annotated:
            f.write(path + line + "\n")

    # Logging informations
    logging.info("(Logging) Found %u annotations.", len(annotated))


if __name__ == "__main__":
    main()
