"""
Utils for Sentinel Hub access
"""

import json

from os import makedirs
from datetime import datetime, timedelta
from typing import Union, Optional, Iterable, List
from glob import glob
from shutil import copyfile, rmtree
import pandas as pd

from .parameters import SUPPORTED_COLLECTION_IDS, SHParameters, OUTPUT_FORMAT
from ...tools.geo_utils import is_bounding_box
from ...tools.time_utils import is_time_interval, get_day_between
from sentinelhub import parse_time


def evaluate_sentinel_parameters(
    time_interval: Union[str, datetime],
    bounding_box: list,
    collection_id: Optional[str] = None,
    output: Optional[str] = None,
    output_needed: Optional[bool] = True,
    parameters: Optional[SHParameters] = None,
) -> None:
    """
    Evaluate parameters for Sentinel Hub access
    """
    if output_needed:
        if not output:
            raise ValueError("Output path must be specified.")
        if parameters and not parameters.OUTPUT_FORMAT:
            raise ValueError("Output format must be specified.")
    if collection_id:
        if collection_id not in SUPPORTED_COLLECTION_IDS:
            raise ValueError(
                f"Collection id {collection_id} is not supported. Supported collections ids are: {SUPPORTED_COLLECTION_IDS}"
            )
    else:
        if not (
            parameters
            and hasattr(parameters, "DATA_COLLECTION")
            and hasattr(parameters.DATA_COLLECTION, "api_id")
        ):
            raise ValueError(f"Data collection is not defined properly.")
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
    if parameters and parameters.MAX_CLOUD_COVERAGE:
        if not isinstance(parameters.MAX_CLOUD_COVERAGE, (int, float)) or (
            parameters.MAX_CLOUD_COVERAGE < 0 or parameters.MAX_CLOUD_COVERAGE > 100
        ):
            raise ValueError("Max cloud coverage must be a number between 0 and 100.")


def imagery_from_tmp_to_dir(
    output_dir: str,
    bounding_box: List[Union[int, float]],
    tmp_dir: Optional[str],
    name: Optional[str] = None,
    bulk: Optional[bool] = False,
    output_format: Optional[str] = OUTPUT_FORMAT.TIFF,
) -> None:
    """
    Copy imagery from tmp to output dir
    """
    format = output_format
    downloaded_files = glob(f"{tmp_dir}/**/response." + format)

    if len(downloaded_files) == 0:
        return
    makedirs(output_dir, exist_ok=True)
    for downloaded_file in downloaded_files:
        request_json = downloaded_file.replace("response." + format, "request.json")
        metadata = generate_raster_metadata(request_json, bounding_box)

        if name and not bulk:
            output_filename = name
        elif name and bulk:
            output_filename = f"{name}_{metadata['acquisition-date']}"
        else:
            if metadata["acquisition-date"]:
                output_filename = f"{metadata['type']}_{metadata['acquisition-date']}"
            else:
                output_filename = metadata["type"]
        copyfile(downloaded_file, f"{output_dir}/{output_filename}." + format)
        with open(f"{output_dir}/{output_filename}.json", "w", encoding="utf-8") as f:
            json.dump(metadata, f)
    rmtree(tmp_dir)


def generate_raster_metadata(request_json: str, bounding_box) -> None:
    """
    Generate metadata for raster
    """
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
        "bounding-box": bounding_box,
        "type": sensor_type,
    }

    return metadata


def filter_times(
    timestamps: Iterable[datetime], time_difference: timedelta
) -> list[datetime]:
    """
    Filters out timestamps within time_difference, preserving only the oldest timestamp.
    """
    timestamps = sorted(set(timestamps))

    filtered_timestamps: list[datetime] = []
    for current_timestamp in timestamps:
        if (
            not filtered_timestamps
            or current_timestamp - filtered_timestamps[-1] > time_difference
        ):
            filtered_timestamps.append(current_timestamp)

    return filtered_timestamps


def stats_to_df(stats_data):
    """Transform Statistical API response into a pandas.DataFrame"""
    df_data = []

    for single_data in stats_data["data"]:
        df_entry = {}
        is_valid_entry = True

        df_entry["interval_from"] = parse_time(single_data["interval"]["from"]).date()
        df_entry["interval_to"] = parse_time(single_data["interval"]["to"]).date()

        for output_name, output_data in single_data["outputs"].items():
            for band_name, band_values in output_data["bands"].items():
                band_stats = band_values["stats"]
                if band_stats["sampleCount"] == band_stats["noDataCount"]:
                    is_valid_entry = False
                    break

                for stat_name, value in band_stats.items():
                    col_name = f"{output_name}_{band_name}_{stat_name}"
                    if stat_name == "percentiles":
                        for perc, perc_val in value.items():
                            perc_col_name = f"{col_name}_{perc}"
                            df_entry[perc_col_name] = perc_val
                    else:
                        df_entry[col_name] = value

        if is_valid_entry:
            df_data.append(df_entry)

    return pd.DataFrame(df_data)
