"""
Utils for Sentinel Hub access
"""

from typing import List


def check_time_interval_is_range(time_interval: List) -> bool:
    """
    """
    if len(time_interval) == 2:   # Suppose it is a simple list, (from-date, to-date)
        if isinstance(time_interval[0], str) and isinstance(time_interval[1], str):
            if time_interval[0] != time_interval[1]:
                return False
    
    return True
