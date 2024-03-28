"""
Created on 3 sty 2020
@author: spasz
"""

import dataclasses
import json
import logging
import os
from datetime import date, datetime, timedelta
from json.decoder import JSONDecodeError


class EnhancedJSONEncoder(json.JSONEncoder):
    """Enhanced JSON encoder with dataclasses support."""

    def default(self, o):
        """Method to default dataclass."""
        # Set : Json
        if isinstance(o, (set)):
            return list(o)

        # Dataclass : Json.
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)

        # Datetime : Json
        if isinstance(o, (datetime, date)):
            return o.isoformat()

        # Timedelta : Json
        if isinstance(o, timedelta):
            return str(o.total_seconds())

        return super().default(o)


def jsonRead(filename: str) -> dict:
    """Reads json as dict."""
    # File not exists
    if not os.path.isfile(filename):
        logging.fatal("(Json) File %s not exists!", filename)
        return {}

    with open(filename, "r") as f:
        try:
            data = json.load(f)
            return data
        except JSONDecodeError:
            logging.error("(Json) Invalid JSON file content!")
            return {}


def jsonWrite(filename: str, data: dict) -> None:
    """Write data dict as json."""
    with open(filename, "w") as f:
        json.dump(data, f, indent=4, sort_keys=False, cls=EnhancedJSONEncoder)


def jsonShow(data: dict):
    """Show json data."""
    logging.info(
        "\n%s\n", json.dumps(data, indent=4, sort_keys=False, cls=EnhancedJSONEncoder)
    )


def jsonToStr(data: dict):
    """Returns string json data."""
    return json.dumps(data, indent=4, sort_keys=False, cls=EnhancedJSONEncoder)


def jsonFromStr(data: str) -> dict:
    """Returns string json data."""
    return json.loads(data)
