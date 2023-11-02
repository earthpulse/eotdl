"""
Data access module for eotdl package.
"""

from .download import download_sentinel_imagery, search_and_download_sentinel_imagery
from .search import search_sentinel_imagery
from .sentinelhub.parameters import SUPPORTED_SENSORS
