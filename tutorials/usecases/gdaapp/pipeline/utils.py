from eotdl.access import find_sentinel_matches_by_bb
from eotdl.access import download_sentinel_imagery

def _find_matches(args):
    bb, date, time_buffer = args
    return find_sentinel_matches_by_bb(bb, date, time_buffer)

def _download_sentinel_imagery(args):
    dir, date, bb, col, name = args
    download_sentinel_imagery(dir, date, bb, col, name)