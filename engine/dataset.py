"""
    Class containing the file dataset informations.

    - Default : Loading 'dataset.txt' file, each line is path to .txt annote file.
    - has method add(path:str) and remove(path:str)
    - has method load() and save()
    - has method is_inside() -> bool
"""

import logging
import os
from typing import Optional


class Dataset:
    """Class containing the file dataset informations."""

    def __init__(self):
        """Init."""
        self._path: Optional[str] = None
        self._dataset: list[str] = []
        self._is_not_saved: bool = False

    def __len__(self):
        """Return length of dataset."""
        return len(self._dataset)

    def add(self, path: str):
        """Add path to dataset."""
        if self.is_inside(path):
            logging.error("Path %s is already in dataset.", path)
            return

        self._dataset.append(path)
        self._is_not_saved = True

    def remove(self, path: str):
        """Remove path from dataset."""
        if not self.is_inside(path):
            logging.error("Path %s is not in dataset.", path)
            return

        self._dataset.remove(path)
        self._is_not_saved = True

    def load(self, path: str):
        """Load dataset from file."""
        self._path = path

        # Check if file exists
        if not os.path.exists(path):
            return

        with open(self._path, "r") as file:
            for line in file:
                self._dataset.append(line.strip())

        self._is_not_saved = False

        # Info
        logging.info("Loaded %d paths from dataset.", len(self._dataset))

    def save(self):
        """Save dataset to file."""
        if self._path is None:
            logging.error("Path is not set.")
            return

        with open(self._path, "w") as file:
            for path in self._dataset:
                file.write(path + "\n")

    def is_inside(self, path: str) -> bool:
        """Check if path is in dataset."""
        return path in self._dataset

    def is_not_saved(self) -> bool:
        """Check if dataset was changed."""
        return self._is_not_saved
