"""
Search imagery
"""

from typing import Union, List
from datetime import datetime

from .sentinelhub import SHClient, SH_PARAMETERS_DICT, evaluate_sentinel_parameters


def search_sentinel_imagery(
    time_interval: Union[str, datetime, List[Union[str, datetime]]],
    bounding_box: List[Union[int, float]],
    sensor: str,
) -> None:
    """
    Search Sentinel imagery
    """
    evaluate_sentinel_parameters(
        sensor, time_interval, bounding_box, output_needed=False
    )

    client = SHClient()
    parameters = SH_PARAMETERS_DICT[sensor]()

    return client.search_data(bounding_box, time_interval, parameters)
