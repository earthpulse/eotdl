"""
STAC utils
"""

from datetime import datetime
from dateutil import parser


def format_time_acquired(dt: str|datetime) -> str:
    """
    """
    dt_str = parser.parse("2021-05-12").strftime('%Y-%m-%dT%H:%M:%S.%f')
    
    return datetime.strptime(dt_str, '%Y-%m-%dT%H:%M:%S.%f')
