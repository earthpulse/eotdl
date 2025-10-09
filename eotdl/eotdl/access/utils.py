def _find_matches(args):
    from .matches import find_sentinel_matches_by_centroid
    ix, centroid, date, time_buffer, width, height, collection_id = args
    return (ix, find_sentinel_matches_by_centroid(centroid, date, time_buffer, width, height, collection_id))

def _download_sentinel_imagery(args):
    from .download import download_sentinel_imagery
    dir, date, bb, col, name = args
    download_sentinel_imagery(dir, date, bb, col, name)