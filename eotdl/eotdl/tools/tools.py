"""
Module for data engineeringt
"""

import re
import tarfile
import datetime
import json
from os.path import exists
from typing import Union, Optional
import geopandas as gpd
import pandas as pd

from shapely.geometry import box
from .geo_utils import get_image_bbox


def get_images_by_location(gdf: gpd.GeoDataFrame, column: str) -> pd.DataFrame:
    """
    Generate a GeoDataFrame with the available images for each location in the dataset.

    :param gdf: GeoDataFrame generated from the ItemCollection of a sen12floods collection
    :return gdf_dates_per_aoi:  GeoDataFrame with the available images for each location in
                                the dataset.
            The returned GeoDataFrame has three columns:
                - location_id: the unique ID of each location.
                - images_count: the count of available images of each location.
                - images_dates: list with the dates of the available images of each location.
    """
    uniques_location_id = gdf[column].unique()  # List of unique location ids
    uniques_location_id.sort()

    images_count_list, images_dates_list = [], []

    # Iterate the unique location ids, count the number of images per location and generate
    # a list with the dates of every image in a location
    for location_id in uniques_location_id:
        dates = gdf[gdf[column] == location_id]["datetime"]
        images_count_list.append(dates.count())
        images_dates_list.append(dates.tolist())

    images_dates_list.sort()  # Sort the list of dates
    data = {
        column: uniques_location_id,
        "dates_count": images_count_list,
        "dates_list": images_dates_list,
    }
    df_dates_per_aoi = pd.DataFrame.from_dict(data)

    return df_dates_per_aoi


def generate_location_payload(
    gdf: Union[gpd.GeoDataFrame, pd.DataFrame], path: str
) -> dict:
    """
    Generate a dictionary with the location payload of the locations in the GeoDataFrame,
    such as the bounding box and the time interval to search for available data.
    """
    payload_cache = f"{path}/location_payload.json"
    if exists(payload_cache):
        # Read as dict
        with open(payload_cache, "r", encoding="utf-8") as f:
            payload = json.load(f)
        return payload

    bbox_date_by_location = {}
    for _, row in gdf.iterrows():
        # Get list from dates_list column
        dates_list = list(row["dates_list"])
        for date in dates_list:
            location_id = row["location_id"]
            date_formatted = datetime.datetime.strptime(
                date, "%Y-%m-%dT%H:%M:%S.%fZ"
            ).strftime("%Y-%m-%d")
            location_id_formatted = f"{location_id}_{date_formatted}"
            bbox_date_by_location[location_id_formatted] = {
                "bounding_box": row["geometry"].bounds,
                # Convert str to datetime
                "time_interval": (date, date),
            }

    # Save to json
    with open(payload_cache, "w", encoding="utf-8") as f:
        json.dump(bbox_date_by_location, f)

    return bbox_date_by_location


def get_tarfile_image_info(
    tar: str,
    path: Optional[str] = None,
    pattern: Optional[str] = r"\d{8}T\d{6}",
    level: Optional[int] = 2,
):
    """
    Generate a GeoDataFrame with the available images for each location in the dataset.
    """
    if path:
        gdf_cache = f"{path}/tarfile_images_info.csv"
        if exists(gdf_cache):
            images_gdf = gpd.read_file(
                gdf_cache, GEOM_POSSIBLE_NAMES="geometry", KEEP_GEOM_COLUMNS="NO"
            )
            images_gdf.set_crs(epsg=4326, inplace=True)

            return images_gdf

    images_df = pd.DataFrame()
    with tarfile.open(tar, "r:gz") as tarf:
        rasters = [
            i for i in tarf.getnames() if i.endswith(".tif") or i.endswith(".tiff")
        ]
        for raster in rasters:
            r = tarf.extractfile(raster)
            bbox = get_image_bbox(r)
            date = extract_image_date_in_folder(raster, pattern)
            image_id = extract_image_id_in_folder(raster, level)
            # Use pd.concat to append to dataframe
            images_df = pd.concat(
                [
                    images_df,
                    pd.DataFrame(
                        {"location_id": [image_id], "datetime": [date], "bbox": [bbox]}
                    ),
                ]
            )

    # Clean duplicates
    images_df = images_df.drop_duplicates(subset=["location_id", "datetime"])
    # Convert to geodataframe
    images_gdf = gpd.GeoDataFrame(
        images_df,
        crs="EPSG:4326",
        geometry=images_df["bbox"].apply(lambda x: box(x[0], x[1], x[2], x[3])),
    )
    # Drop bbox column
    images_gdf = images_gdf.drop(columns=["bbox"])
    # Set crs
    images_gdf = images_gdf.set_crs(epsg=4326)
    # Sort by location_id
    images_gdf = images_gdf.sort_values(by=["location_id"])
    if path:
        # Save to csv
        images_gdf.to_csv(gdf_cache, index=False)

    return images_gdf


def extract_image_date_in_folder(raster_path: str, pattern: str):
    """
    Extract the date from the folder name of the image.
    """
    case = re.findall(pattern, raster_path)

    if case:
        date = case[0]
        # Convert date to format YYYY-MM-DDT00:00:00.000Z as datetime object
        formatted_date = datetime.datetime.strptime(date, "%Y%m%dT%H%M%S").strftime(
            "%Y-%m-%dT%H:%M:%S.%fZ"
        )
        return formatted_date

    return None


def extract_image_id_in_folder(raster_path: str, level: int):
    """
    Extract the location id from the folder name of the image, given the level of the folder.
    """
    return raster_path.split("/")[level]


def format_product_location_payload(
    location_payload: dict, images_response: dict, all_info: bool = False
) -> dict:
    """
    Format the location payload with the images response.
    """
    for _, _ in location_payload.items():
        # Add new key to the dictionary
        if all_info:
            location_payload[id]["image"] = (
                images_response[id] if id in images_response else None
            )
        else:
            location_payload[id]["image"] = (
                images_response[id]["properties"]["id"] if images_response[id] else None
            )

    return location_payload
