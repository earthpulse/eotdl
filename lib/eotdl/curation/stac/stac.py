"""
Module for generating STAC metadata 
"""

import pystac

from shapely.geometry import Polygon, mapping


def create_stac_item(metadata_json: str,
                     extensions: list
                     ) -> pystac.Item:
    """
    """
    bbox = None
        
    # Create geojson feature
    geom = mapping(Polygon([
        
    ]))

    # Instantiate pystac item
    item = pystac.Item()

    # Enable item extensions
    for extension in extensions:
        item.ext.enable(extension)

    return item
