"""
Module for EO-TDL metadata
"""

import datetime
import json
import rasterio
from rasterio.warp import transform_bounds

from os.path import dirname, join, exists


def generate_raster_metadata(raster_path: str,
                             output_folder: str,
                             date_adquired: str|datetime.datetime
                             ) -> None:
    """
    Generate metadata.json file for a raster file

    :param raster_path: path to the raster file
    :param output_folder: output folder to write the metadata.json file to
    :param date_adquired: date adquired of the raster file
    """
    with rasterio.open(raster_path) as ds:
        bounds = ds.bounds
        dst_crs = 'EPSG:4326'  # EPSG identifier for WGS84 coordinate system used by the geojson format
        left, bottom, right, top = rasterio.warp.transform_bounds(ds.crs, dst_crs, *bounds)
        bbox = [left, bottom, right, top]

    # Get raster directory path to get the request.json file
    raster_dir_path = dirname(raster_path)

    # Read the request.json file and get the request data type
    if exists(raster_dir_path):
        with open(join(raster_dir_path, 'request.json'), 'r') as f:
            request = json.load(f)
            request_data_type = request['request']['payload']['input']['data'][0]['type']

    metadata_path = join(output_folder, 'metadata.json')
    metadata = {'date-adquired': date_adquired, 'bounding-box': bbox, 'type': request_data_type}
    
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f)
