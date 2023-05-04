"""
Module for generating STAC metadata 
"""

import json
import pystac
import rasterio

from datetime import datetime
from shapely.geometry import Polygon, mapping


class STACGenerator:

    def __init__(self):
        pass

    def create_stac_catalog(self):
        """
        """
        pass

    def create_stac_collection(self):
        """
        """
        pass

    def create_stac_item(self,
                        tiff_path: str,
                        metadata_json: str,
                        extensions: list
                        ) -> pystac.Item:
        """
        """
        with open(metadata_json, "r") as f:
            metadata = json.load(f)
        
        with rasterio.open(tiff_path) as ds:
            
            bounds = ds.bounds
            src_crs = ds.crs
            dst_crs = 'EPSG:4326'  # EPSG identifier for WGS84 coordinate system used by the geojson format
            
            left, bottom, right, top = rasterio.warp.transform_bounds(ds.crs, dst_crs, *bounds)
            bbox = [left, bottom, right, top]
            
            # Create geojson feature
            geom = mapping(Polygon([
            [left, bottom],
            [left, top],
            [right, top],
            [right, bottom]
            ]))

            bbox = None
                
            # Create geojson feature
            geom = mapping(Polygon([
            [left, bottom],
            [left, top],
            [right, top],
            [right, bottom]
            ]))
            
            try:
                time_acquired = datetime.strptime(metadata_json["date-adquired"], '%Y-%m-%dT%H:%M:%S.%f')
            except KeyError:
                return
            
            # Instantiate pystac item
            item = pystac.Item(id=metadata_json["id"],
                    geometry=geom,
                    bbox=bbox,
                    datetime = time_acquired,
                    properties={
                    })

            # Enable item extensions
            for extension in extensions:
                item.ext.enable(extension)

            return item
