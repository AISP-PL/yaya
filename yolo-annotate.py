#!/usr/bin/python3
import cv2
import numpy as np
from helpers.selector import *

if __name__ == '__main__' :

    # Read image
    im = cv2.imread("input/image.png")

    # Select ROI
    r = select_roi('Selector',im)

    # Crop image
    imCrop = im[int(r[1]):int(r[1]+r[3]), int(r[0]):int(r[0]+r[2])]

    # Display cropped image
    cv2.imshow("Image", imCrop)
    cv2.waitKey(0)
