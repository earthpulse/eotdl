from eotdl.access import find_sentinel_matches_by_centroid
from eotdl.access import download_sentinel_imagery

def _find_matches(args):
    ix, centroid, date, time_buffer, width, height, collection_id = args
    return (ix, find_sentinel_matches_by_centroid(centroid, date, time_buffer, width, height, collection_id))

def _download_sentinel_imagery(args):
    dir, date, bb, col, name = args
    download_sentinel_imagery(dir, date, bb, col, name)