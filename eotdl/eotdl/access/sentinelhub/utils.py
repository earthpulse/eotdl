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
from ...tools.geo_utils import is_bounding_box, get_image_bbox
from ...tools.time_utils import is_time_interval, get_day_between


def evaluate_sentinel_parameters(
    sensor: str,
    time_interval: Union[str, datetime],
    bounding_box: list,
    output: Optional[str] = None,
    output_needed: Optional[bool] = True,
) -> None:
    """
    Evaluate parameters for Sentinel Hub access
    """
    if output_needed:
        if not output:
            raise ValueError("Output path must be specified.")
    if sensor not in SUPPORTED_SENSORS:
        raise ValueError(
            f"Sensor {sensor} is not supported. Supported sensors are: {SUPPORTED_SENSORS}"
        )
    if not time_interval:
        raise ValueError("Time interval must be specified.")
    else:
        if len(time_interval) == 2 and not is_time_interval(time_interval):
            raise ValueError(
                "Time interval must be a list or tuple with two elements in format YYYY-MM-DD."
            )
    if not bounding_box:
        raise ValueError("Bounding box must be specified.")
    else:
        if not is_bounding_box(bounding_box):
            raise ValueError(
                "Bounding box must be a list or tuple with four elements in format (lon_min, lat_min, lon_max, lat_max)."
            )


def imagery_from_tmp_to_dir(
    output_dir: str, tmp_dir: Optional[str] = "/tmp/sentinelhub"
) -> None:
    """
    Copy imagery from tmp to output dir
    """
    downloaded_files = glob(f"{tmp_dir}/**/response.tiff")
    if len(downloaded_files) == 0:
        return

    makedirs(output_dir, exist_ok=True)

    for downloaded_file in downloaded_files:
        request_json = downloaded_file.replace("response.tiff", "request.json")
        metadata = generate_raster_metadata(downloaded_file, request_json)
        if metadata["acquisition-date"]:
            output_filename = f"{metadata['type']}_{metadata['acquisition-date']}"
        else:
            output_filename = metadata["type"]

        copyfile(downloaded_file, f"{output_dir}/{output_filename}.tif")
        with open(f"{output_dir}/{output_filename}.json", "w", encoding="utf-8") as f:
            json.dump(metadata, f)

    rmtree(tmp_dir)


def generate_raster_metadata(raster: str, request_json: str) -> None:
    """
    Generate metadata for raster
    """
    bbox = get_image_bbox(raster)
    with open(request_json, "r", encoding="utf-8") as f:
        json_content = json.load(f)

    payload_data = json_content["request"]["payload"]["input"]["data"][0]
    sensor_type = payload_data["type"]
    # Get day between from and to
    if "timeRange" in payload_data["dataFilter"] and sensor_type != "dem":
        time_range = payload_data["dataFilter"]["timeRange"]
        acquisition_date = get_day_between(time_range["from"], time_range["to"])
    else:  # DEM data does not have a timeRange
        acquisition_date = None

    metadata = {
        "acquisition-date": acquisition_date,
        "bounding-box": bbox,
        "type": sensor_type,
    }

    return metadata
