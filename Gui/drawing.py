'''
Created on 23 lis 2020

@author: spasz
'''
import cv2
import random
import Gui.colors as colors


def DrawDetections(image, detections, colors):
    ''' Draw all detections.'''
    for detection in detections:
        label, confidence, bbox = detection
        left, top, right, bottom = bbox
        cv2.rectangle(image, (left, top), (right, bottom), colors[label], 1)
        cv2.putText(image, '{} [{:.2f}]'.format(label, float(confidence)),
                    (left+2, bottom - 3), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                    (0, 0, 0), 2)
        cv2.putText(image, '{} [{:.2f}]'.format(label, float(confidence)),
                    (left, bottom - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                    (255, 255, 255), 1)
    return image


def DrawText(image, text, pos, font=cv2.FONT_HERSHEY_SIMPLEX, scale=1, color=colors.white, thickness=1, bgColor=None, bgMargin=5):
    ''' Drawing text method with background.'''
    (width, height), baseline = cv2.getTextSize(text, font, scale, thickness)
    if (bgColor is not None):
        x, y = pos
        image = cv2.rectangle(image, (x-bgMargin, y+bgMargin),
                              (x+width+bgMargin, y-height-bgMargin), bgColor, -1)
    cv2.putText(image, text, pos, font, scale, color, thickness)
    return (width+bgMargin, height+bgMargin)


def CreateColors(names):
    """
    Create a dict with one random BGR color for each
    class name
    """
    return {name: (
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255)) for name in names}
