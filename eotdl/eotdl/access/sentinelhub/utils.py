"""
Utils for Sentinel Hub access
"""

from datetime import datetime
from typing import List


def check_time_interval_is_range(time_interval: List) -> bool:
    """
    """
    if len(time_interval) != 2:
        return False
    
    for e in time_interval:
        if not isinstance(e, (str, datetime)):
            return False
    
    return True
