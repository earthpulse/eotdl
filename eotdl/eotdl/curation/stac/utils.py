"""
STAC utils
"""

import pystac
import json

from os.path import dirname, join, exists
from os import listdir
from datetime import datetime
from dateutil import parser
from pandas import isna
from typing import Union


def format_time_acquired(dt: Union[str, datetime]) -> str:
    """
    Format the date time to the required format for STAC

    :param dt: date time to format
    """
    dt_str = parser.parse(dt).strftime("%Y-%m-%dT%H:%M:%S.%f")

    # convert the string to datetime object
    dt_obj = datetime.strptime(dt_str, "%Y-%m-%dT%H:%M:%S.%f")

    return dt_obj


def count_ocurrences(text: str, text_list: list) -> int:
    """
    Count the number of ocurrences of a string in a list of strings

    :param text: string to count the ocurrences
    """
    count = 0
    for string in text_list:
        if text in string:
            count += 1
    return count


def convert_df_geom_to_shape(row):
    """
    Convert the geometry of a dataframe row to a shapely shape

    :param row: row of a dataframe
    """
    from shapely.geometry import shape

    if not isna(row["geometry"]):
        geo = shape(row["geometry"])
        wkt = geo.wkt
    else:
        wkt = "POLYGON EMPTY"

    return wkt


def get_all_children(obj: pystac.STACObject) -> list:
    """
    Get all the children of a STAC object

    :param obj: STAC object
    """
    children = []

    # Append the current object to the list
    children.append(obj.to_dict())

    # Collections
    collections = list(obj.get_collections())

    for collection in collections:
        children.append(collection.to_dict())

    # Items
    items = obj.get_items()
    for item in items:
        children.append(item.to_dict())

    # Items from collections
    for collection in collections:
        items = collection.get_items()
        for item in items:
            children.append(item.to_dict())

    return children


def cut_images(images_list: Union[list, tuple]) -> list:
    """
    """
    dirnames = list()
    images = list()

    for image in images_list:
        dir = dirname(image)
        if dir not in dirnames:
            dirnames.append(dir)
            images.append(image)

    return images


def get_item_metadata(raster_path: str) -> str:
    """
    Get the metadata JSON file of a given directory, associated to a raster file

    :param raster_path: path to the raster file
    """
    # Get the directory of the raster file
    raster_dir_path = dirname(raster_path)
    # Get the metadata JSON file
    # Check if there is a metadata.json file in the directory
    if 'metadata.json' in listdir(raster_dir_path):
        metadata_json = join(raster_dir_path, 'metadata.json')
    else:
        # If there is no metadata.json file in the directory, check if there is
        # a json file with the same name as the raster file
        raster_name = raster_path.split('/')[-1]
        raster_name = raster_name.split('.')[0]
        metadata_json = join(raster_dir_path, f'{raster_name}.json')
        if not exists(metadata_json):
            # If there is no metadata.json file in the directory, return None
            return None
    
    # Open the metadata.json file and return it
    with open(metadata_json, 'r') as f:
        metadata = json.load(f)
    
    return metadata
