#!/usr/bin/python3
import cv2
import numpy as np
import logging
import argparse
import sys
import engine.annote as annote
from engine.annoter import *
from helpers.files import *
from helpers.textAnnotations import *
from yolohelpers.distribution import Distribution

# Arguments and config
parser = argparse.ArgumentParser()
parser.add_argument('-i', '--input', type=str,
                    required=True, help='Input path')
parser.add_argument('-r', '--rename', type=str,
                    required=False, help='Rename class number `class0` to `class1`. class0:class1')
parser.add_argument('-cc', '--checks', action='store_true',
                    required=False, help='Extra checks of data')
parser.add_argument('-sb', '--sortBy', type=int, nargs='?', const=0, default=0,
                    required=False, help='Sort by method number (0 None, 1 Datetime, 2 Alphabet)')
parser.add_argument('-oc', '--onlyClass', type=int,
                    required=False, help='Only specific class number')
parser.add_argument('-on', '--onlyNewFiles', action='store_true',
                    required=False, help='Process only files without detections file.')
parser.add_argument('-v', '--verbose', action='store_true',
                    required=False, help='Show verbose finded and processed data')
args = parser.parse_args()

# Check - input argument
if (args.input is None):
    print('Error! No arguments!')
    sys.exit(-1)

# Check - files filter
isOnlyNewFiles = False
if (args.onlyNewFiles):
    isOnlyNewFiles = True

# Check - files filter
isOnlySpecificClass = None
if (args.onlyClass is not None):
    isOnlySpecificClass = args.onlyClass

# Enabled logging
if (__debug__ is True):
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
else:
    logging.basicConfig(stream=sys.stderr, level=logging.INFO)
logging.debug('Logging enabled!')

d = Distribution(args.input,
                 args.rename,
                 args.checks)
d.Save(args.input)
