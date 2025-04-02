"""
Search imagery
"""

from typing import Union, List
from datetime import datetime

from .sentinelhub import (
    SHClient,
    get_default_parameters,
    evaluate_sentinel_parameters,
    SHParameters,
    supports_cloud_coverage,
)


def search_sentinel_imagery(
    time_interval: Union[str, datetime, List[Union[str, datetime]]],
    bounding_box: List[Union[int, float]],
    collection_id: str,
) -> None:
    """
    Search Sentinel imagery
    """
    evaluate_sentinel_parameters(
        time_interval, bounding_box, collection_id, output_needed=False
    )
    parameters = get_default_parameters(collection_id)
    client = SHClient(parameters.BASE_URL)
    return client.search_data(bounding_box, time_interval, parameters)


def advanced_imagery_search(
    time_interval: Union[str, datetime, List[Union[str, datetime]]],
    bounding_box: List[Union[int, float]],
    parameters: SHParameters,
) -> None:
    """
    Advanced imagery search
    """
    evaluate_sentinel_parameters(
        time_interval, bounding_box, output_needed=False, parameters=parameters
    )

    if (
        supports_cloud_coverage(parameters.DATA_COLLECTION.api_id)
        and parameters.MAX_CLOUD_COVERAGE
    ):
        parameters.FILTER = "eo:cloud_cover < " + str(parameters.MAX_CLOUD_COVERAGE)

    client = SHClient(parameters.BASE_URL)
    return client.search_data(bounding_box, time_interval, parameters)
