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
parser.add_argument('-va', '--verifyAnnotations', action='store_true',
                    required=False, help='Verify/Check of text annotations.')
parser.add_argument('-vi', '--verifyImages', action='store_true',
                    required=False, help='Verify/Check of images.')
parser.add_argument('-sb', '--sortBy', type=int, nargs='?', const=0, default=0,
                    required=False, help='Sort by method number (0 None, 1 Datetime, 2 Alphabet)')
parser.add_argument('-oc', '--onlyClass', type=int,
                    required=False, help='Only specific class number')
parser.add_argument('-on', '--onlyNewFiles', action='store_true',
                    required=False, help='Process only files without detections file.')
parser.add_argument('-sh', '--showcase', action='store_true',
                    required=False, help='Creates visual showcase report')
parser.add_argument('-v', '--verbose', action='store_true',
                    required=False, help='Show verbose finded and processed data')
args = parser.parse_args()


# Enabled logging
if (__debug__ is True):
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
else:
    logging.basicConfig(stream=sys.stderr, level=logging.INFO)
logging.debug('Logging enabled!')

d = Distribution(args)
d.Save(args.input)
