"""
Module for generating STAC metadata 
"""

import json
from typing import Optional
import pystac
import rasterio
from rasterio.warp import transform_bounds

from datetime import datetime
from shapely.geometry import Polygon, mapping
from glob import glob

from .utils import format_time_acquired


class STACGenerator:

    def create_stac_catalog(self):
        """
        """
        pass

    def create_stac_collection(self):
        """
        """
        pass

    def create_stac_item(self,
                        tiff_dir_path: str,
                        metadata_json: str,
                        extensions: Optional[list] = None
                        ) -> pystac.Item:
        """
        """
        with open(metadata_json, "r") as f:
            metadata = json.load(f)

        bbox = metadata['bounding-box']
        left, bottom, right, top = bbox

        # Create geojson feature
        geom = mapping(Polygon([
        [left, bottom],
        [left, top],
        [right, top],
        [right, bottom]
        ]))

        try:
            time_acquired = format_time_acquired(metadata["date-adquired"])
        except KeyError:
            return
        
        # Instantiate pystac item
        item = pystac.Item(id='test',
                geometry=geom,
                bbox=bbox,
                datetime = time_acquired,
                properties={
                })

        # Enable item extensions
        if extensions:
            for extension in extensions:
                item.ext.enable(extension)

        rasters = glob(f'{tiff_dir_path}/*.tif*')

        for raster in rasters:
            href = raster.split('/')[-1]
            title = href.split('.')[-2]
            type = "image/tiff; application=geotiff"
            asset = pystac.Asset(href=href, title=title, media_type=type)
            item.add_asset(title, asset)

        return item
