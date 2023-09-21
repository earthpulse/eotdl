'''
Time utils
'''

from typing import Union
from datetime import datetime
from dateutil import parser


def format_time_acquired(dt: Union[str, datetime]) -> str:
    """
    Format the date time to the required format for STAC

    :param dt: date time to format
    """
    dt_str = parser.parse(dt).strftime("%Y-%m-%dT%H:%M:%S.%f")

    # convert the string to datetime object
    dt_obj = datetime.strptime(dt_str, "%Y-%m-%dT%H:%M:%S.%f")

    return dt_obj
