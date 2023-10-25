from .sentinelhub import SHClient
from .sentinelhub.parameters import SH_PARAMETERS_DICT
from .sentinelhub.utils import evaluate_sentinel_parameters
from .search import search_imagery

from shutil import rmtree
from datetime import datetime
from typing import Union, List


def download_sentinel_imagery(output: str,
                              sensor: str,
                              time_interval: Union[str, datetime, List[Union[str, datetime]]],
                              bounding_box: List[Union[int, float]]
                              ) -> None:
    evaluate_sentinel_parameters(output, sensor, time_interval, bounding_box)

    client = SHClient()
    parameters = SH_PARAMETERS_DICT[sensor]()

    request = client.request_data(time_interval, bounding_box, parameters)
    client.download_data(request)
    rmtree(client.tmp_dir)


def search_and_download_sentinel_imagery(output: str,
                                         sensor: str,
                                         time_interval: Union[str, datetime, List[Union[str, datetime]]],
                                         bounding_box: List[Union[int, float]]
                                         ) -> None:
    evaluate_sentinel_parameters(output, sensor, time_interval, bounding_box)

    client = SHClient()
    parameters = SH_PARAMETERS_DICT[sensor]()

    results = search_imagery(sensor, time_interval, bounding_box)
    timestamps = [date.strftime("%Y-%m-%d") for date in results.get_timestamps()]

    requests_list = list()
    for date in timestamps:
        requests_list.append(client.request_data(date, bounding_box, parameters))
    client.download_data(requests_list)
