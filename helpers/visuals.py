'''
    Dataclass with image visual properties
    analyzed from image array.
'''
from __future__ import annotations
from dataclasses import asdict, dataclass, field
import os
import cv2
import numpy as np
import imagehash
from PIL import Image

from helpers.files import ChangeExtension
from helpers.json import jsonRead, jsonWrite


@dataclass
class Visuals:
    ''' Dataclass with visual properties of image. '''
    # Path to analyzed image
    imagepath: str = field(init=True, default=None)
    # Image width
    width: float = field(init=True, default=0)
    # Image height
    height: float = field(init=True, default=0)
    # Hue - dominant hue color
    hue: float = 0
    # Saturation of colors 0 to 1.0
    saturation: float = 0
    # Brightness from 0 to 1.0
    brightness: float = 0
    # Diffrential (perceptual) hash of image
    dhash: str = 0

    def __post_init__(self):
        ''' Post initiliatizaton.'''

    def Save(self):
        ''' Save data to file.'''
        # Check : Not existing image
        if (self.imagepath is None):
            return

        # Create visuals annotations json filepath.
        jsonpath = ChangeExtension(self.imagepath, '.visuals.json')

        # Save data to json file.
        jsonWrite(jsonpath, asdict(self))

    @staticmethod
    def LoadCreate(imagepath: str, force: bool = False) -> Visuals:
        ''' Load or create visuals from image.'''

        # 1. Load from json file
        loaded = Visuals.Load(imagepath)
        if (loaded is not None) and (not force):
            return loaded

        # 2. Otherwise create and save
        visuals = Visuals.Create(imagepath)
        visuals.Save()

        return visuals

    @staticmethod
    def Load(imagepath: str) -> Visuals:
        ''' Load visuals from image annotations json file.'''
        # Create visuals annotations json filepath.
        jsonpath = ChangeExtension(imagepath, '.visuals.json')
        if (not os.path.exists(jsonpath)):
            return None

        # Load json dict.
        json = jsonRead(jsonpath)
        return Visuals(**json)

    @staticmethod
    def Create(imagepath: str) -> Visuals:
        ''' Create visuals from image.'''
        # Check : Not existing image, empty visuals
        if (not os.path.exists(imagepath)):
            return Visuals(imagepath=imagepath)

        # Load/Check image
        image = cv2.imread(imagepath)
        if (image is None):
            return Visuals(imagepath=imagepath)

        # Get image size
        height, width, _ = image.shape

        # Obliczenie średniej jasności, saturacji oraz barwy
        image_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        hue = np.mean(image_hsv[:, :, 0])  # Średnia barwa (hue)
        saturation = np.mean(image_hsv[:, :, 1])  # Średnia saturacja
        brightness = np.mean(image_hsv[:, :, 2])  # Średnia jasność

        # Image hash : Calculate hash of image
        image_pil = Image.fromarray(image)
        dhash = imagehash.dhash(image_pil, hash_size=6)
        dhash_normalized = int(str(dhash), 16) / (16**9)

        return Visuals(imagepath=imagepath,
                       width=width,
                       height=height,
                       hue=hue,
                       saturation=saturation,
                       brightness=brightness,
                       dhash=dhash_normalized
                       )
