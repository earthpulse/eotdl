'''
Metadata utilities for STAC
'''

import json

from os.path import dirname, join, exists, basename
from os import listdir


def get_item_metadata(raster_path: str) -> str:
    """
    Get the metadata JSON file of a given directory, associated to a raster file

    :param raster_path: path to the raster file
    """
    # Get the directory of the raster file
    raster_dir_path = dirname(raster_path)
    # Get the metadata JSON file
    # Check if there is a metadata.json file in the directory
    if 'metadata.json' in listdir(raster_dir_path):
        metadata_json = join(raster_dir_path, 'metadata.json')
    else:
        # If there is no metadata.json file in the directory, check if there is
        # a json file with the same name as the raster file
        raster_name = basename(raster_path).split('.')[0]
        metadata_json = join(raster_dir_path, f'{raster_name}.json')
        if not exists(metadata_json):
            # If there is no metadata file in the directory, return None
            return None
    
    # Open the metadata file and return it
    with open(metadata_json, 'r') as f:
        metadata = json.load(f)
    
    return metadata
