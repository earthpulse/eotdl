from .sentinelhub import SHClient
from .sentinelhub.parameters import (SUPPORTED_SENSORS, SH_PARAMETERS_DICT)
from typing import Optional


def search_sentinel_imagery(sensor: str,
                   time_interval: Optional[list] = None,
                   bounding_box: Optional[list] = None
                   ) -> None:
    if sensor not in SUPPORTED_SENSORS:
        raise ValueError(f"Sensor {sensor} is not supported. Supported sensors are: {SUPPORTED_SENSORS}")

    client = SHClient()
    parameters = SH_PARAMETERS_DICT[sensor]()

    return client.search_data(bounding_box, time_interval, parameters)
