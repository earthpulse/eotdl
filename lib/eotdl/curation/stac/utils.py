"""
STAC utils
"""

from datetime import datetime
from dateutil import parser


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
    from shapely.geometry import shape

    geo = shape(row['geometry'])
    wkt = geo.wkt
    
    return wkt