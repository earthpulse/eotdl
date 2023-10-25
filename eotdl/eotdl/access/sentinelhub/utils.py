"""
Utils for Sentinel Hub access
"""

from datetime import datetime
from typing import Union, Optional
from .parameters import SUPPORTED_SENSORS
from ...tools.geo_utils import is_bounding_box
from ...tools.time_utils import is_time_interval


def evaluate_sentinel_parameters(sensor: str,
                                 time_interval: Union[str, datetime],
                                 bounding_box: list,
                                 output: Optional[str] = None,
                                 output_needed: Optional[bool] = True
                                 ) -> None:
    """
    """
    if output_needed:
        if not output:
            raise ValueError("Output path must be specified.")
    if sensor not in SUPPORTED_SENSORS:
        raise ValueError(f"Sensor {sensor} is not supported. Supported sensors are: {SUPPORTED_SENSORS}")
    if not time_interval:
        raise ValueError("Time interval must be specified.")
    else:
        if not is_time_interval(time_interval):
            raise ValueError(f"Time interval must be a list or tuple with two elements in format YYYY-MM-DD.")
    if not bounding_box:
        raise ValueError("Bounding box must be specified.")
    else:
        if not is_bounding_box(bounding_box):
            raise ValueError(f"Bounding box must be a list or tuple with four elements in format (lon_min, lat_min, lon_max, lat_max).")
