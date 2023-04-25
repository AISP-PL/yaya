'''
    Dataclass with image visual properties
    analyzed from image array.
'''
from __future__ import annotations
from dataclasses import asdict, dataclass, field
import os
import cv2
import numpy as np

from helpers.files import ChangeExtension
from helpers.json import jsonRead, jsonWrite


@dataclass
class Visuals:
    ''' Dataclass with visual properties of image. '''
    # Path to analyzed image
    imagepath : str = field(init=True, default = None)
    # Hue - dominant hue color
    hue : float = 0
    # Saturation of colors 0 to 1.0
    saturation : float = 0
    # Brightness from 0 to 1.0
    brightness : float = 0


    def __post_init__(self):
        ''' Post initiliatizaton.'''

    def Save(self):
        ''' Save data to file.'''
        # Check : Not existing image
        if (self.imagepath is None):
            return

        # Create visuals annotations json filepath.
        jsonpath = ChangeExtension(self.imagepath,'.visuals.json')

        # Save data to json file.
        jsonWrite(jsonpath, asdict(self))


    @staticmethod
    def LoadCreate(imagepath : str) -> Visuals:
        ''' Load or create visuals from image.'''

        # 1. Load from json file
        loaded = Visuals.Load(imagepath)
        if (loaded is not None):
            return loaded
        
        # 2. Otherwise create
        return Visuals.Create(imagepath)


    @staticmethod
    def Load(imagepath: str) -> Visuals:
        ''' Load visuals from image annotations json file.'''
        # Create visuals annotations json filepath.
        jsonpath = ChangeExtension(imagepath,'.visuals.json')
        if (not os.path.exists(jsonpath)):
            return None

        # Load json dict.
        json = jsonRead(jsonpath)
        return Visuals(**json)

    @staticmethod
    def Create(imagepath : str) -> Visuals:
        ''' Create visuals from image.'''
        # Check : Not existing image
        if (not os.path.exists(imagepath)):
            return None
            
        # Load image and convert HSV
        image = cv2.imread(imagepath)
        image_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # Obliczenie średniej jasności, saturacji oraz barwy
        hue = np.mean(image_hsv[:, :, 0])  # Średnia barwa (hue)
        saturation = np.mean(image_hsv[:, :, 1])  # Średnia saturacja
        brightness = np.mean(image_hsv[:, :, 2])  # Średnia jasność

        return Visuals(imagepath=imagepath,
                       hue=hue,
                       saturation=saturation,
                       brightness=brightness)
        