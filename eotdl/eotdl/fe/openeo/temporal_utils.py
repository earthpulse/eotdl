import pandas as pd
from typing import List

def compute_temporal_extent(start_date: str, nb_months: int) -> List[str]:
    """Compute temporal extent based on a start date and duration in months.

    Args:
        start_date (str): Start date in 'YYYY-MM-DD' format.
        nb_months (int): Number of months from the start date.

    Returns:
        List[str]: Temporal extent as [start_date, end_date].
    """
    start = pd.to_datetime(start_date)
    end = start + pd.DateOffset(months=nb_months)
    return [start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d')]