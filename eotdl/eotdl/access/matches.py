from datetime import datetime, timedelta

from ..access import search_sentinel_imagery
from ..tools import bbox_from_centroid

def find_sentinel_matches_by_centroid(centroid, date, time_buffer, width, height, collection_id="sentinel-2-l2a"):
    dates = [(date - timedelta(days=time_buffer/2)).strftime('%Y-%m-%d'),
             (date + timedelta(days=time_buffer/2)).strftime('%Y-%m-%d')]
    custom_bbox = bbox_from_centroid(x=centroid.y, y=centroid.x, pixel_size=10, width=width, height=height)
    sentinel_matches = list(search_sentinel_imagery(dates, custom_bbox, collection_id))
    return sentinel_matches

def find_sentinel_matches_by_bb(bb, date, time_buffer, collection_id="sentinel-2-l2a"):
    if isinstance(date, str):
        date = datetime.strptime(date, '%Y-%m-%d')
    dates = [(date - timedelta(days=time_buffer/2)).strftime('%Y-%m-%d'),
             (date + timedelta(days=time_buffer/2)).strftime('%Y-%m-%d')]
    sentinel_matches = list(search_sentinel_imagery(dates, bb, collection_id))
    return sentinel_matches