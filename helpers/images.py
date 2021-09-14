'''
Created on 10 paź 2020

@author: spasz
'''
import cv2
import logging


def PointRescale(point, ratio):
    ''' Rescale point by ratio.'''
    x, y = point
    return int(x*ratio), int(y*ratio)


def GetResizedHeightToWidth(width, height, maxWidth=1280):
    ''' Returns resized values.'''
    ratio = 1
    if (width > maxWidth):
        ratio = maxWidth/width
        height = int(ratio*height)-1
        width = maxWidth

    return width, height, ratio


def GetResizedWidthToHeight(width, height, maxHeight=1080):
    ''' Returns resized values.'''
    ratio = 1
    if (height > maxHeight):
        ratio = maxHeight/height
        width = int(ratio*width)-1
        height = maxHeight

    return width, height, ratio


def ResizeToMaxWidth(image, maxWidth=1280):
    ''' Resize image with handling aspect ratio.'''
    height, width = image.shape[:2]
    width, height, ratio = GetResizedHeightToWidth(width, height, maxWidth)
    return cv2.resize(image, (width, height), interpolation=cv2.INTER_AREA), ratio


def ResizeToHeight(image, maxHeight=1080):
    ''' Resize image with handling aspect ratio.'''
    height, width = image.shape[:2]
    width, height, ratio = GetResizedWidthToHeight(width, height, maxHeight)
    return cv2.resize(image, (width, height), interpolation=cv2.INTER_AREA), ratio
