"""
Download imagery
"""

from datetime import datetime, timedelta
from typing import Union, List, Optional

from .sentinelhub import (
    SHClient,
    evaluate_sentinel_parameters,
    imagery_from_tmp_to_dir,
    get_default_parameters,
    SHParameters,
    filter_times,
)
from .search import advanced_imagery_search


def download_sentinel_imagery(
    output: str,
    time_interval: Union[str, datetime, List[Union[str, datetime]]],
    bounding_box: List[Union[int, float]],
    collection_id: str,
    name: Optional[str] = None,
) -> None:
    """
    Download Sentinel imagery
    """
    evaluate_sentinel_parameters(time_interval, bounding_box, collection_id, output)
    parameters = get_default_parameters(collection_id)
    return advanced_imagery_download(
        output, time_interval, bounding_box, parameters, name
    )


def advanced_imagery_download(
    output: str,
    time_interval: Union[str, datetime, List[Union[str, datetime]]],
    bounding_box: List[Union[int, float]],
    parameters: SHParameters,
    name: Optional[str] = None,
) -> None:
    """
    Advanced imagery download
    """
    evaluate_sentinel_parameters(
        time_interval, bounding_box, output=output, parameters=parameters
    )
    client = SHClient(parameters.BASE_URL)

    results = advanced_imagery_search(time_interval, bounding_box, parameters)
    timestamps = results.get_timestamps()
    time_difference = timedelta(hours=1)
    filtered_timestamps = filter_times(timestamps, time_difference)

    requests_list = []
    for date in filtered_timestamps:
        timestamp_interval = (date - time_difference, date + time_difference)
        requests_list.append(
            client.request_data(timestamp_interval, bounding_box, parameters)
        )
    if len(requests_list) == 0:
        print(
            f"No images found for {parameters.DATA_COLLECTION.api_id} in the specified time: {time_interval}"
        )
        return
    elif len(requests_list) <= 2:
        bulk = False
    else:
        bulk = True

    client.download_data(requests_list)
    imagery_from_tmp_to_dir(
        output,
        bounding_box,
        client.tmp_dir,
        name=name,
        bulk=bulk,
        output_format=parameters.OUTPUT_FORMAT.value,
    )


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
