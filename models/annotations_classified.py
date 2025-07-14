from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd
from numpy.typing import NDArray


@dataclass
class AnnotationsClassifiedBool:
    """
    Class to handle classified annotations.
    """

    # Filenames : String array
    filenames: NDArray[np.str_] = field(default_factory=lambda: np.array([], dtype=str))
    # Class IDs : Integer array
    class_ids: NDArray[np.int16] = field(
        default_factory=lambda: np.array([], dtype=np.int16)
    )
    # Detections xywh as float32 [
    x: NDArray[np.float32] = field(
        default_factory=lambda: np.array([], dtype=np.float32)
    )
    y: NDArray[np.float32] = field(
        default_factory=lambda: np.array([], dtype=np.float32)
    )
    w: NDArray[np.float32] = field(
        default_factory=lambda: np.array([], dtype=np.float32)
    )
    h: NDArray[np.float32] = field(
        default_factory=lambda: np.array([], dtype=np.float32)
    )
    # Classified bools : True /False
    bools: NDArray[np.bool_] = field(default_factory=lambda: np.array([], dtype=bool))

    @property
    def filenames_unique(self) -> NDArray[np.str_]:
        """
        Get unique filenames from the classified annotations.
        """
        return np.unique(self.filenames)

    def has_filename(self, filename: str) -> bool:
        """
        Check if the filename exists in the classified annotations.
        """
        return bool(np.any(self.filenames == filename))

    def get_filenames_where(self, result: bool) -> NDArray[np.str_]:
        """
        Get filenames where the classified bool matches the result.
        """
        return self.filenames[self.bools == result]

    @staticmethod
    def from_csv(path: str) -> AnnotationsClassifiedBool:
        """
        Load classified annotations from CSV file.
        """
        df = pd.read_csv(path, sep=";", decimal=",")
        return AnnotationsClassifiedBool(
            filenames=df["filename"].to_numpy(dtype=str),
            class_ids=df["class_id"].to_numpy(dtype=int),
            x=df["x"].to_numpy(dtype=np.float32),
            y=df["y"].to_numpy(dtype=np.float32),
            w=df["w"].to_numpy(dtype=np.float32),
            h=df["h"].to_numpy(dtype=np.float32),
            bools=df["bool"].to_numpy(dtype=bool),
        )

    def to_csv(self, path: str) -> None:
        """
        Save classified annotations to CSV file.
        """

        df = pd.DataFrame(
            {
                "filename": self.filenames,
                "class_id": self.class_ids,
                "x": self.x,
                "y": self.y,
                "w": self.w,
                "h": self.h,
                "bool": self.bools,
            }
        )
        df.to_csv(path, index=False, sep=";", decimal=",", header=True)

    def append(
        self, filename: str, class_id: int, xywh: np.ndarray, bool_value: bool
    ) -> None:
        """
        Append a new classified annotation.
        """
        self.filenames = np.append(self.filenames, filename)
        self.class_ids = np.append(self.class_ids, class_id)
        self.bools = np.append(self.bools, bool_value)
        self.x = np.append(self.x, xywh[0])
        self.y = np.append(self.y, xywh[1])
        self.w = np.append(self.w, xywh[2])
        self.h = np.append(self.h, xywh[3])
