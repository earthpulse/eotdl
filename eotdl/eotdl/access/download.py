"""
Download imagery
"""

from datetime import datetime
from typing import Union, List

from .sentinelhub import (
    SHClient,
    SH_PARAMETERS_DICT,
    evaluate_sentinel_parameters,
    imagery_from_tmp_to_dir,
)
from .search import search_sentinel_imagery


def download_sentinel_imagery(
    output: str,
    time_interval: Union[str, datetime, List[Union[str, datetime]]],
    bounding_box: List[Union[int, float]],
    sensor: str,
) -> None:
    """
    Download Sentinel imagery
    """
    evaluate_sentinel_parameters(sensor, time_interval, bounding_box, output)

    client = SHClient()
    parameters = SH_PARAMETERS_DICT[sensor]()

    request = client.request_data(time_interval, bounding_box, parameters)
    client.download_data(request)
    imagery_from_tmp_to_dir(output)


def search_and_download_sentinel_imagery(
    output: str,
    time_interval: Union[str, datetime, List[Union[str, datetime]]],
    bounding_box: List[Union[int, float]],
    sensor: str,
) -> None:
    """
    Search and download Sentinel imagery
    """
    evaluate_sentinel_parameters(sensor, time_interval, bounding_box, output)

    client = SHClient()
    parameters = SH_PARAMETERS_DICT[sensor]()

    results = search_sentinel_imagery(time_interval, bounding_box, sensor)
    timestamps = [date.strftime("%Y-%m-%d") for date in results.get_timestamps()]

    requests_list = []
    for date in timestamps:
        requests_list.append(client.request_data(date, bounding_box, parameters))
    client.download_data(requests_list)
    imagery_from_tmp_to_dir(output)
