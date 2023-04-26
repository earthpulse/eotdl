"""
Utils module
"""
from datetime import datetime, timedelta

def get_time_interval_from_date(date: str) -> list:
    """
    """
    _date = datetime.strptime(date, '%Y-%m-%d').date()
    _previous = _date - timedelta(days=1)
    previous= _previous.strftime('%Y-%m-%d')

    return previous, date
