"""
Module for EO-TDL metadata
"""

import datetime
import json
import rasterio
from rasterio.warp import transform_bounds

from os.path import dirname, join


def generate_raster_metadata(raster_path: str,
                             output_folder: str,
                             date_adquired: str|datetime.datetime
                             ) -> None:
    """
    """
    with rasterio.open(raster_path) as ds:
        bounds = ds.bounds
        dst_crs = 'EPSG:4326'  # EPSG identifier for WGS84 coordinate system used by the geojson format
        left, bottom, right, top = rasterio.warp.transform_bounds(ds.crs, dst_crs, *bounds)
        bbox = [left, bottom, right, top]

    metadata_path = join(output_folder, 'metadata.json')
    metadata = {'date-adquired': date_adquired, 'bounding-box': bbox}
    
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f)
