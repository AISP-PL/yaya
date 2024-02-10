"""
    Session dataclass which holds the session timestamp and other program
    session data.
"""

import os
import shutil
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from helpers.files import ChangeExtension


@dataclass
class Session:
    """Session dataclass."""

    # Timestamp : When the session was started
    timestamp: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """Post-init operations. Session starts automatically."""

    @property
    def session_path(self) -> str:
        """Session directory."""
        return f"temp/session_{self.timestamp.strftime('%Y%m%d_%H%M')}"

    def fileentry_store(self, fileEntry: dict):
        """Copy image from path to sesion.

        Example file entry :
        --------------------
                {
                    "Name": filename,
                    "Path": path + filename,
                    "ID": index,
                    "IsAnnotation": isAnnotation,
                    "Annotations": txtAnnotations,
                    "AnnotationsClasses": ",".join(
                        {f"{item.classNumber}" for item in txtAnnotations}
                    ),
                    "Datetime": os.lstat(path + filename).st_mtime,
                    "Errors": len(self.errors),
                    "Detections": detections,
                    "Metrics": metrics,
                    "Visuals": visuals,
                }
            )

        """
        # Mkdir : Create directory if not exists
        Path(self.session_path).mkdir(parents=True, exist_ok=True)

        # Image : Copy
        session_image_path = f"{self.session_path}/{fileEntry['Name']}"
        shutil.copy(fileEntry["Path"], session_image_path)

        # Annotations : Copy (.txt file)
        annotations_path = ChangeExtension(fileEntry["Path"], ".txt")
        session_annotations_path = ChangeExtension(session_image_path, ".txt")
        if os.path.exists(annotations_path):
            shutil.copy(annotations_path, session_annotations_path)

        # Detector : Copy (.detector file)
        detector_path = ChangeExtension(fileEntry["Path"], ".detector")
        session_detector_path = ChangeExtension(session_image_path, ".detector")
        if os.path.exists(detector_path):
            shutil.copy(detector_path, session_detector_path)

        # Visuals : Copy (.visuals file)
        visuals_path = ChangeExtension(fileEntry["Path"], ".visuals")
        session_visuals_path = ChangeExtension(session_image_path, ".visuals")
        if os.path.exists(visuals_path):
            shutil.copy(visuals_path, session_visuals_path)

        return fileEntry
