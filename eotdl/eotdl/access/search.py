from .sentinelhub import SHClient
from .sentinelhub.parameters import SH_PARAMETERS_DICT
from .sentinelhub.utils import evaluate_sentinel_parameters
from typing import Optional


def search_sentinel_imagery(sensor: str,
                            time_interval: Optional[list] = None,
                            bounding_box: Optional[list] = None
                            ) -> None:
    evaluate_sentinel_parameters(sensor, time_interval, bounding_box, output_needed=False)

    client = SHClient()
    parameters = SH_PARAMETERS_DICT[sensor]()

    return client.search_data(bounding_box, time_interval, parameters)
