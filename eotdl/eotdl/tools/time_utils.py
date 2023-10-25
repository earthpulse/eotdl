import geopandas as gpd
import pandas as pd

from datetime import datetime, timedelta
from typing import Union, Optional, List


def is_time_interval(time_interval: list) -> bool:
    if not isinstance(time_interval, (list, tuple)) or len(time_interval) != 2:
        return False
    
    for value in time_interval:
        if not isinstance(value, str):
            return False
        if not is_valid_date(value):
            return False

    return True


def is_valid_date(date_str: str) -> bool:
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def get_first_last_dates(dataframe: Union[pd.DataFrame, gpd.GeoDataFrame], dates_column: Optional[str] = 'datetime'):
    """
    """
    dataframe[dates_column] = dataframe[dates_column].apply(lambda x: sorted(x))
    dataframe['first_date'] = dataframe['dates_list'].apply(lambda x: x[0])
    dataframe['last_date'] = dataframe['dates_list'].apply(lambda x: x[-1])
    dataframe = dataframe.sort_values(by=['first_date', 'last_date'])
    # Sort by sequence id
    dataframe = dataframe.sort_values(by=['location_id'])
    # Convert first_date and last_date to datetime, in format YYYY-MM-DD
    dataframe['first_date'] = pd.to_datetime(dataframe['first_date'], format='%Y-%m-%d')
    dataframe['last_date'] = pd.to_datetime(dataframe['last_date'], format='%Y-%m-%d')

    return dataframe


def create_time_slots(start_date: datetime, end_date: datetime, n_chunks: int):
    """
    """
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, "%Y-%m-%d")
    tdelta = (end_date - start_date) / n_chunks
    edges = [(start_date + i * tdelta).date().isoformat() for i in range(n_chunks)]
    slots = [(edges[i], edges[i + 1]) for i in range(len(edges) - 1)]

    return slots


def expand_time_interval(time_interval: Union[list, tuple], format: str='%Y-%m-%dT%H:%M:%S.%fZ') -> list:
    """
    """
    start_date = time_interval[0]
    end_date = time_interval[1]

    if isinstance(start_date, str):
        start_date = datetime.datetime.strptime(start_date, format)
    if isinstance(end_date, str):
        end_date = datetime.datetime.strptime(end_date, format)

    # Add one day to start date and remove one day to end date
    new_start_date = start_date - datetime.timedelta(days=1)
    new_end_date = end_date + datetime.timedelta(days=1)

    # Convert to string
    new_start_date = new_start_date.strftime(format)
    new_end_date = new_end_date.strftime(format)

    return new_start_date, new_end_date


def prepare_time_interval(date):
    if isinstance(date, str):
        date = datetime.strptime(date, "%Y-%m-%d")
    elif isinstance(date, datetime):
        date = date.strftime("%Y-%m-%d")
    elif isinstance(date, tuple):
        if not is_time_interval(date):
            raise ValueError('The time interval must be a range of two dates, with format YYYY-MM-DD or a datetime object')
        else:
            return date
    else:
        raise ValueError('The date must be a string with format YYYY-MM-DD or a datetime object')
    date_day_before = date - timedelta(days=1)
    date_next_day = date + timedelta(days=1)
    date_day_before = date_day_before.strftime("%Y-%m-%d")
    date_next_day = date_next_day.strftime("%Y-%m-%d")

    return (date_day_before, date_next_day)


def get_day_between(from_date: Union[datetime, str], 
                    to_date: Union[datetime, str]
                    ) -> str:
    """
    """
    if isinstance(from_date, str):
        from_date = datetime.strptime(from_date, "%Y-%m-%dT%H:%M:%SZ")
    if isinstance(to_date, str):
        to_date = datetime.strptime(to_date, "%Y-%m-%dT%H:%M:%SZ")

    date_between = from_date + timedelta(days=1)
    date_between = date_between.strftime("%Y-%m-%d") 
    
    return date_between
