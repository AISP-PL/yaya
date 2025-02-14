"""
    Dataclass with image visual properties
    analyzed from image array.
"""

from __future__ import annotations

import os
from dataclasses import asdict, dataclass, field
from typing import Optional

import cv2
import imagehash
import numpy as np
from PIL import Image

from helpers.files import ChangeExtension
from helpers.json import jsonRead, jsonWrite


@dataclass
class Visuals:
    """Dataclass with visual properties of image."""

    # Path to analyzed image
    imagepath: str = field(init=True, default=None)
    # Image width
    width: float = field(init=True, default=0)
    # Image height
    height: float = field(init=True, default=0)
    # Grid 20x20 of tuples(h,s,v) of image informations
    grid: list[tuple[float, float, float]] = field(init=True, default_factory=list)
    # Diffrential (perceptual) hash of image
    dhash: str = 0
    # True if it's duplicate of other image
    isDuplicate: bool = False

    def __post_init__(self) -> None:
        """Post initiliatizaton."""

    @property
    def hue(self) -> float:
        """Returns average hue of image."""
        value = np.mean([item[0] for item in self.grid])
        return float(value) if not np.isnan(value) else 0.0

    @property
    def saturation(self) -> float:
        """Returns average saturation of image."""
        value = np.mean([item[1] for item in self.grid])
        return float(value) if not np.isnan(value) else 0.0

    @property
    def brightness(self) -> float:
        """Returns average brightness of image."""
        value = float(np.mean([item[2] for item in self.grid]))
        return float(value) if not np.isnan(value) else 0.0

    @property
    def numpy_grid(self) -> np.ndarray:
        """Returns grid as numpy array."""
        array = np.array(self.grid)
        if array.size == 0:
            return np.zeros((20, 20, 3))

        array = array.reshape((20, 20, 3))
        # Replace NaN as zeroes
        array = np.nan_to_num(array, copy=False, nan=0.0)
        return array

    def Save(self):
        """Save data to file."""
        # Check : Not existing image
        if self.imagepath is None:
            return

        # Create visuals annotations json filepath.
        jsonpath = ChangeExtension(self.imagepath, ".visuals.json")

        # Save data to json file.
        jsonWrite(jsonpath, asdict(self))

    @staticmethod
    def LoadCreate(imagepath: str, force: bool = False) -> Visuals:
        """Load or create visuals from image."""

        # 1. Load from json file
        loaded = Visuals.Load(imagepath)
        if (loaded is not None) and (not force):
            return loaded

        # 2. Otherwise create and save
        visuals = Visuals.Create(imagepath)
        visuals.Save()

        return visuals

    @staticmethod
    def Load(imagepath: str) -> Optional[Visuals]:
        """Load visuals from image annotations json file."""
        # Create visuals annotations json filepath.
        jsonpath = ChangeExtension(imagepath, ".visuals.json")
        if not os.path.exists(jsonpath):
            return None

        # Load json dict.
        json = jsonRead(jsonpath)
        try:
            return Visuals(**json)
        except Exception:
            return None

    @staticmethod
    def Create(imagepath: str) -> Visuals:
        """Create visuals from image."""
        # Check : Not existing image, empty visuals
        if not os.path.exists(imagepath):
            return Visuals(imagepath=imagepath)

        # Load/Check image
        image = cv2.imread(imagepath)
        if image is None:
            return Visuals(imagepath=imagepath)

        # Get image size
        height, width, _ = image.shape

        image_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        # Grid : Calculate HSV of every grid part
        grid: list[tuple[float, float, float]] = []
        for row in range(20):
            for col in range(20):
                # Get grid part
                grid_part = image_hsv[
                    row * height // 20 : (row + 1) * height // 20,
                    col * width // 20 : (col + 1) * width // 20,
                ]

                # Calculate mean of HSV
                h = np.mean(grid_part[:, :, 0])
                s = np.mean(grid_part[:, :, 1])
                v = np.mean(grid_part[:, :, 2])

                # Add to grid
                grid.append((h, s, v))

        # Image hash : Calculate hash of image
        image_pil = Image.fromarray(image)
        dhash = imagehash.dhash(image_pil, hash_size=6)
        dhash_normalized = int(str(dhash), 16) / (16**9)

        return Visuals(
            imagepath=imagepath,
            width=width,
            height=height,
            grid=grid,
            dhash=dhash_normalized,
        )


@dataclass
class VisualsDuplicates:
    """Dataclass for visuals duplicates finder."""

    # Dictionary with hashes : visuals
    visuals: dict = field(init=True, default_factory=dict)

    def __post_init__(self):
        """Post initiliatizaton."""

    def Add(self, visuals: Visuals):
        """Add visuals to dictionary."""
        # Check : Invalid visuals
        if visuals is None:
            return

        # Add visuals to dictionary
        self.visuals[visuals.dhash] = visuals

    def IsDuplicate(self, visuals: Visuals) -> bool:
        """Check if visuals is duplicate of other image."""
        # Check : Invalid visuals
        if visuals is None:
            return False

        # Check : Duplicate
        if visuals.dhash not in self.visuals:
            return False

        # Check : HSV
        other = self.visuals[visuals.dhash]
        return (
            (visuals.hue == other.hue)
            and (visuals.saturation == other.saturation)
            and (visuals.brightness == other.brightness)
        )
