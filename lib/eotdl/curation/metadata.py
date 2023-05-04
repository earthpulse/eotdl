"""
Module for EO-TDL metadata
"""

import datetime
import json

from os.path import dirname, join


def generate_raster_metadata(raster_path: str,
                             output_folder: str,
                             date_adquired: str|datetime.datetime
                             ) -> None:
    """
    """
    # Maintain the raster path parameter, as in the future could be 
    # useful for raster related info
    metadata_path = join(output_folder, 'metadata.json')
    metadata = {'date-adquired': date_adquired}
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f)
