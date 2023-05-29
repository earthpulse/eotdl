"""
Module for data engineering with STAC elements
"""
import geopandas as gpd
from pystac import ItemCollection


def stac_items_to_gdf(items: ItemCollection) -> gpd.GeoDataFrame:
    """
    Get a GeoDataFrame from a given pystac.ItemCollection. 

    :param: items: A pystac.ItemCollection
    :return: GeoDataframe from the given ItemCollection
    """
    _features = [i.to_dict() for i in items]

    # Get a new ItemCollection by removing duplicate items, if they exist
    features = []
    for f in _features:
        if f not in features:
            features.append(f)
    
    return gpd.GeoDataFrame.from_features(features)