from .sentinelhub import SHClient
from .sentinelhub.parameters import (SUPPORTED_SENSORS, SH_PARAMETERS_DICT)
from .search import search_imagery

from shutil import rmtree
from datetime import datetime
from typing import Union


def download_sentinel_imagery(output: str,
                     sensor: str,
                     time_interval: Union[str, datetime],
                     bounding_box: list
                     ) -> None:
    if not output:
        raise ValueError("Output path must be specified.")
    if sensor not in SUPPORTED_SENSORS:
        raise ValueError(f"Sensor {sensor} is not supported. Supported sensors are: {SUPPORTED_SENSORS}")

    client = SHClient()
    parameters = SH_PARAMETERS_DICT[sensor]()

    request = client.request_data(time_interval, bounding_box, parameters)
    client.download_data(request)
    rmtree(client.tmp_dir)


def search_and_download_sentinel_imagery(output: str,
                                sensor: str,
                                time_interval: Union[str, datetime],
                                bounding_box: list
                                ) -> None:
    if not output:
        raise ValueError("Output path must be specified.")
    if sensor not in SUPPORTED_SENSORS:
        raise ValueError(f"Sensor {sensor} is not supported. Supported sensors are: {SUPPORTED_SENSORS}")

    client = SHClient()
    parameters = SH_PARAMETERS_DICT[sensor]()

    results = search_imagery(sensor, time_interval, bounding_box)
    timestamps = [date.strftime("%Y-%m-%d") for date in results.get_timestamps()]

    requests_list = list()
    for date in timestamps:
        requests_list.append(client.request_data(date, bounding_box, parameters))
    client.download_data(requests_list)
