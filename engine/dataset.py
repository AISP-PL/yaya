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

    def __init__(self) -> None:
        """Init."""
        # Path
        self._path: Optional[str] = None
        # Dataset
        self._dataset: set[str] = set()
        # Is not saved
        self._is_not_saved: bool = False

    def __len__(self) -> int:
        """Return length of dataset."""
        return len(self._dataset)

    def add(self, path: str) -> None:
        """Add path to dataset."""
        if self.is_inside(path):
            logging.error("Path %s is already in dataset.", path)
            return

        self._dataset.add(path)
        self._is_not_saved = True

    def remove(self, path: str) -> None:
        """Remove path from dataset."""
        if not self.is_inside(path):
            logging.error("Path %s is not in dataset.", path)
            return

        self._dataset.remove(path)
        self._is_not_saved = True

    def load(self, path: str) -> None:
        """Load dataset from file."""
        # Validation file path
        self._path = path
        # Validation directory path
        directory_path = os.path.dirname(path)

        # Check if file exists
        if not os.path.exists(path):
            return

        # Validation file : Read all lines
        is_any_removed: bool = False
        with open(self._path, "r") as file:
            for line in file:
                # Full filepath : Create
                filepath = os.path.join(directory_path, line.strip())

                # Check : File exists
                if not os.path.exists(filepath):
                    logging.warning("File %s does not exists. Removed.", filepath)
                    is_any_removed = True
                    continue

                self._dataset.add(line.strip())

        self._is_not_saved = False
        if is_any_removed:
            self.save()

        # Info
        logging.info("Loaded %d paths from dataset.", len(self._dataset))

    def save(self) -> None:
        """Save dataset to file."""
        if self._path is None:
            logging.error("Path is not set.")
            return

        # Create : Sorted list of paths
        sorted_paths = sorted(self._dataset)

        with open(self._path, "w") as file:
            for path in sorted_paths:
                file.write(path + "\n")

        self._is_not_saved = False
        logging.info("Saved %d paths to dataset %s.", len(self._dataset), self._path)

    def is_inside(self, path: str) -> bool:
        """Check if path is in dataset."""
        return path in self._dataset

    def is_not_saved(self) -> bool:
        """Check if dataset was changed."""
        return self._is_not_saved
