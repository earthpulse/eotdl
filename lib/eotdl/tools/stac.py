"""
Module for data engineering with STAC elements
"""
import geopandas as gpd
from pystac import ItemCollection


def stac_items_to_gdf(items: ItemCollection) -> gpd.GeoDataFrame:
    """
    Get a GeoDataFrame from a given PySTAC.ItemCollection
    :param: items: A PySTAC.ItemCollection
    :return: GeoDataframe from the given ItemCollection
    """
    _features = [i.to_dict() for i in items]

    # Get a new ItemCollection by removing duplicate items, if they exist
    features = []
    for f in _features:
        if f not in features:
            features.append(f)
            
    # Add the location_id as a property, in order to retrieve it as a column 
    # in the GeoDataFrame
    for f in features:
        location_id = f['id'].split('_')[3]
        f['properties']['location_id'] = location_id
    
    return gpd.GeoDataFrame.from_features(features)
