"""
Download imagery
"""

from datetime import datetime
from typing import Union, List, Optional

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
    name: Optional[str] = None,
) -> None:
    """
    Download Sentinel imagery
    """
    evaluate_sentinel_parameters(sensor, time_interval, bounding_box, output)

    client = SHClient()
    parameters = SH_PARAMETERS_DICT[sensor]()

    results = search_sentinel_imagery(time_interval, bounding_box, sensor)
    timestamps = [date.strftime("%Y-%m-%d") for date in results.get_timestamps()]

    requests_list = []
    for date in timestamps:
        requests_list.append(client.request_data(date, bounding_box, parameters))
    if len(requests_list) == 0:
        print(f"No images found for {sensor} in the specified time: {time_interval}")
        return
    elif len(requests_list) <= 2:
        bulk = False
    else:
        bulk = True
    client.download_data(requests_list)
    imagery_from_tmp_to_dir(output, name=name, bulk=bulk)


def search_and_download_sentinel_imagery(
    output: str,
    time_interval: Union[str, datetime, List[Union[str, datetime]]],
    bounding_box: List[Union[int, float]],
    sensor: str,
) -> None:
    """
    Search and download Sentinel imagery
    """
    from warnings import warn

    warn(
        "The function `search_and_download_sentinel_imagery` has been deprecated and will be removed in future updates. Please use download_satellite_imagery instead."
    )
    download_sentinel_imagery(output, time_interval, bounding_box, sensor)
