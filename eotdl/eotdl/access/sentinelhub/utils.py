"""
Utils for Sentinel Hub access
"""

import json

from os import makedirs
from datetime import datetime
from typing import Union, Optional
from glob import glob
from shutil import copyfile, rmtree

from .parameters import SUPPORTED_SENSORS
from ...tools.geo_utils import is_bounding_box
from ...tools.time_utils import is_time_interval, get_day_between


def evaluate_sentinel_parameters(sensor: str,
                                 time_interval: Union[str, datetime],
                                 bounding_box: list,
                                 output: Optional[str] = None,
                                 output_needed: Optional[bool] = True
                                 ) -> None:
    """
    """
    if output_needed:
        if not output:
            raise ValueError("Output path must be specified.")
    if sensor not in SUPPORTED_SENSORS:
        raise ValueError(f"Sensor {sensor} is not supported. Supported sensors are: {SUPPORTED_SENSORS}")
    if not time_interval:
        raise ValueError("Time interval must be specified.")
    else:
        if not is_time_interval(time_interval):
            raise ValueError(f"Time interval must be a list or tuple with two elements in format YYYY-MM-DD.")
    if not bounding_box:
        raise ValueError("Bounding box must be specified.")
    else:
        if not is_bounding_box(bounding_box):
            raise ValueError(f"Bounding box must be a list or tuple with four elements in format (lon_min, lat_min, lon_max, lat_max).")


def imagery_from_tmp_to_dir(output_dir: str,
                            tmp_dir: Optional[str] = '/tmp/sentinelhub'
                            ) -> None:
    """
    """
    downloaded_files = glob(f"{tmp_dir}/**/response.tiff")
    assert len(downloaded_files) > 0, "No files downloaded"

    makedirs(output_dir, exist_ok=True)

    for downloaded_file in downloaded_files:
        downloaded_json = downloaded_file.replace('response.tiff', 'request.json')
        json_content = json.load(open(downloaded_json))
        sensor_type = json_content['request']['payload']['input']['data'][0]['type']
        # Get day between from and to
        time_range = json_content['request']['payload']['input']['data'][0]['dataFilter']['timeRange']
        timestamp = get_day_between(time_range['from'], time_range['to'])
        output_filename = f"{sensor_type}_{timestamp}"

        for file, format in zip([downloaded_file, downloaded_json], ['tif', 'json']):
            output_file = f"{output_dir}/{output_filename}.{format}"
            copyfile(file, output_file)
    
    rmtree(tmp_dir)
