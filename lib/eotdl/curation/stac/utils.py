"""
STAC utils
"""

import pystac

from datetime import datetime
from dateutil import parser
from pandas import isna
from numpy import nan


def format_time_acquired(dt: str|datetime) -> str:
    """
    Format the date time to the required format for STAC
    
    :param dt: date time to format
    """
    dt_str = parser.parse(dt).strftime('%Y-%m-%dT%H:%M:%S.%f')

    # convert the string to datetime object
    dt_obj = datetime.strptime(dt_str, '%Y-%m-%dT%H:%M:%S.%f')
    
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

    if not isna(row['geometry']):
        geo = shape(row['geometry'])
        wkt = geo.wkt
    else:
        wkt = 'POLYGON EMPTY'
    
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


stac_collection = {
    'crs': 4326,
    'properties': {
                "type": "character varying",
                "description": "character varying",
                "extent": "character varying",
                "license": "character varying",
                "collection": "character varying",
                "stac_version": "character varying",
                "providers": "character varying",
                "properties": "character varying",
                "stac_id": "character varying",
                "links": "character varying",
                "assets": "character varying",
                "bbox": "character varying",
                "stac_extensions": "character varying"
            }
}