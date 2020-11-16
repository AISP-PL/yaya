#!/usr/bin/python3
import cv2
import numpy as np
import logging
import argparse
import sys
from helpers.selector import *
from helpers.files import *
from ObjectDetectors.DetectorYOLOv4COCO import DetectorYOLOv4COCO
from ObjectDetectors.DetectorYOLOv4custom import DetectorYOLOv4custom

# Arguments and config
parser = argparse.ArgumentParser()
parser.add_argument('-i', '--input', type=str,
                    required=True, help='Input path')
parser.add_argument('-o', '--output', type=str, nargs='?', const='', default='',
                    required=False, help='Output subdirectory name')
parser.add_argument('-ar', '--augmentation', action='store_true',
                    required=False, help='Process extra image augmentation.')
parser.add_argument('-v', '--verbose', action='store_true',
                    required=False, help='Show verbose finded and processed data')
args = parser.parse_args()

if (args.input is None):
    print('Error! No arguments!')
    sys.exit(-1)

# Enabled logging
if (__debug__ is True):
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
else:
    logging.basicConfig(stream=sys.stderr, level=logging.INFO)
logging.debug('Logging enabled!')


excludes = ['.', '..', './', '.directory']
dirpath = args.input
filenames = os.listdir(dirpath)

# Step 0 - filter only images
filenames = [f for f in filenames if (f not in excludes) and (IsImageFile(f))]

# Step 1 - process all images
for f in filenames:
    # Read image
    im = cv2.imread(dirpath+f)

    # Select ROI
    r = select_roi('Selector',im)

    # Crop image
    imCrop = im[int(r[1]):int(r[1]+r[3]), int(r[0]):int(r[0]+r[2])]

    # Display cropped image
    cv2.imshow("Image", imCrop)
    cv2.waitKey(0)
