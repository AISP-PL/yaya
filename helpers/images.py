'''
Created on 10 paź 2020

@author: spasz
'''
import cv2
import logging


def GetResizedHeightToWidth(width, height, maxWidth=1280):
    ''' Returns resized values.'''
    if (width > maxWidth):
        ratio = maxWidth/width
        height = int(ratio*height)-1
        width = maxWidth

    return width, height


def ResizeToWidth(image, maxWidth=1280):
    ''' Resize image with handling aspect ratio.'''
    height, width = image.shape[:2]
    width, height = GetResizedHeightToWidth(width, height, maxWidth)
    return cv2.resize(image, (width, height), interpolation=cv2.INTER_AREA)
