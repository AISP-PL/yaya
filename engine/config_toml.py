"""
This module reads the config file and stores the data in a dictionary.
"""

import os
import sys

from helpers.Singleton import Singleton

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

from typing import Any, Dict


class ConfigToml(metaclass=Singleton):
    """.toml config file reader"""

    def __init__(self, path: str = "config.toml") -> None:
        """Constructor"""
        # Data : Config data dictionary
        self.data: Dict[str, Any] = {}

        # Load : Load the config file
        if self.load(path) is True:
            return

        # Fallback to config.example.toml
        if self.load("config.example.toml") is True:
            return

        raise FileNotFoundError("Config file not found!")

    def load(self, path: str) -> bool:
        """Load the config .toml file"""
        if not os.path.exists(path):
            return False

        with open(path, "rb") as f:
            try:
                self.data = tomllib.load(f)
                return True

            except tomllib.TOMLDecodeError as e:
                sys.exit(f"Config file has invalid format. {e}")

        return False

    def get(self, key: str, default: Any = None) -> Any:
        """Get the value of a key with a default fallback"""
        return self.data.get(key, default)

    def __getitem__(self, key: str) -> Any:
        """Get the value of a key"""
        try:
            return self.data[key]

        except KeyError:
            sys.exit(f"Config file is misconfigured. Missing {key}")
