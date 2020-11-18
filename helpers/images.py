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


def GetResizedWidthToHeight(width, height, maxHeight=1080):
    ''' Returns resized values.'''
    if (height > maxHeight):
        ratio = maxHeight/height
        width = int(ratio*height)-1
        height = maxHeight

    return width, height


def ResizeToWidth(image, maxWidth=1280):
    ''' Resize image with handling aspect ratio.'''
    height, width = image.shape[:2]
    width, height = GetResizedHeightToWidth(width, height, maxWidth)
    return cv2.resize(image, (width, height), interpolation=cv2.INTER_AREA)


def ResizeToHeight(image, maxHeight=1080):
    ''' Resize image with handling aspect ratio.'''
    height, width = image.shape[:2]
    width, height = GetResizedWidthToHeight(width, height, maxHeight)
    return cv2.resize(image, (width, height), interpolation=cv2.INTER_AREA)
