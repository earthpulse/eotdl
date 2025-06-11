"""
Statistics
"""

from datetime import datetime
from typing import Union, List
import pandas as pd

from .sentinelhub import (
    SHClient,
    evaluate_sentinel_parameters,
    SHParameters,
    stats_to_df,
)


def get_statistics(
    time_interval: Union[str, datetime, List[Union[str, datetime]]],
    bounding_box: List[Union[int, float]],
    parameters: SHParameters,
    evalscript: str,
) -> None:
    """
    Download Sentinel imagery
    """
    client = SHClient(parameters.BASE_URL)

    parameters.EVALSCRIPT = evalscript
    evaluate_sentinel_parameters(
        time_interval, bounding_box, parameters=parameters, output_needed=False
    )
    req = client.requestStatistics(time_interval, bounding_box, parameters)
    stat_data = client.download_statistical_data(req)
    dfs = [stats_to_df(stats) for stats in stat_data]
    return pd.concat(dfs)
