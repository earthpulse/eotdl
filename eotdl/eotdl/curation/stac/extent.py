'''
Module for STAC extent
'''

import pystac
from datetime import datetime
import rasterio
import json

from glob import glob
from os.path import dirname
from typing import List

from .utils import get_item_metadata


def get_dem_temporal_interval() -> pystac.TemporalExtent:
    """
    Get a temporal interval for DEM data
    """
    min_date = datetime.strptime('2011-01-01', '%Y-%m-%d')
    max_date = datetime.strptime('2015-01-07', '%Y-%m-%d')

    return pystac.TemporalExtent([(min_date, max_date)])
    
def get_unknow_temporal_interval() -> pystac.TemporalExtent:
    """
    Get an unknown temporal interval
    """
    min_date = datetime.strptime('2000-01-01', '%Y-%m-%d')
    max_date = datetime.strptime('2023-12-31', '%Y-%m-%d')

    return pystac.TemporalExtent([(min_date, max_date)])
    
def get_unknow_extent() -> pystac.Extent:
    """
    """
    return pystac.Extent(spatial=pystac.SpatialExtent([[0, 0, 0, 0]]),
                         temporal=pystac.TemporalExtent([(datetime.strptime('2000-01-01', '%Y-%m-%d'), 
                                                          datetime.strptime('2023-12-31', '%Y-%m-%d')
                                                          )]))


def get_collection_extent(rasters: List[str]) -> pystac.Extent:
    """
    Get the extent of a collection
    
    :param rasters: list of rasters
    """
    # Get the spatial extent of the collection
    spatial_extent = get_collection_spatial_extent(rasters)
    # Get the temporal interval of the collection
    temporal_interval = get_collection_temporal_interval(rasters)
    # Create the Extent object
    extent = pystac.Extent(spatial=spatial_extent, temporal=temporal_interval)

    return extent
    
def get_collection_spatial_extent(rasters: List[str]) -> pystac.SpatialExtent:
    """
    Get the spatial extent of a collection

    :param path: path to the directory
    """
    # Get the bounding boxes of all the given rasters
    bboxes = list()
    for raster in rasters:
        with rasterio.open(raster) as ds:
            bounds = ds.bounds
            dst_crs = 'EPSG:4326'
            try:
                left, bottom, right, top = rasterio.warp.transform_bounds(ds.crs, dst_crs, *bounds)
                bbox = [left, bottom, right, top]
            except rasterio.errors.CRSError:
                spatial_extent = pystac.SpatialExtent([[0, 0, 0, 0]])
                return spatial_extent
            bboxes.append(bbox)
    # Get the minimum and maximum values of the bounding boxes
    try:
        left = min([bbox[0] for bbox in bboxes])
        bottom = min([bbox[1] for bbox in bboxes])
        right = max([bbox[2] for bbox in bboxes])
        top = max([bbox[3] for bbox in bboxes])
        spatial_extent = pystac.SpatialExtent([[left, bottom, right, top]])
    except ValueError:
        spatial_extent = pystac.SpatialExtent([[0, 0, 0, 0]])
    finally:
        return spatial_extent

def get_collection_temporal_interval(rasters: List[str]) -> pystac.TemporalExtent:
    """
    Get the temporal interval of a collection

    :param path: path to the directory
    """
    # Get all the metadata.json files in the directory of all the given rasters
    metadata_jsons = list()
    for raster in rasters:
        metadata_json = get_item_metadata(raster)
        if metadata_json:
            metadata_jsons.append(metadata_json)

    if not metadata_jsons:
        return get_unknow_temporal_interval()   # If there is no metadata, set a generic temporal interval
    
    # Get the temporal interval of every metadata.json file and the type of the data
    data_types = list()
    temporal_intervals = list()
    for metadata in metadata_jsons:
        # Append the temporal interval to the list as a datetime object
        temporal_intervals.append(metadata['acquisition-date']) if metadata['acquisition-date'] else None
        # Append the data type to the list
        data_types.append(metadata['type']) if metadata['type'] else None
        
    if temporal_intervals:
        try:
            # Get the minimum and maximum values of the temporal intervals
            min_date = min([datetime.strptime(interval, '%Y-%m-%d') for interval in temporal_intervals])
            max_date = max([datetime.strptime(interval, '%Y-%m-%d') for interval in temporal_intervals])
        except ValueError:
            min_date = datetime.strptime('2000-01-01', '%Y-%m-%d')
            max_date = datetime.strptime('2023-12-31', '%Y-%m-%d')
        finally:
            # Create the temporal interval
            return pystac.TemporalExtent([(min_date, max_date)])
    else:
        # Check if the collection is composed by DEM data. If not, set a generic temporal interval
        if set(data_types) == {'dem'} or set(data_types) == {'DEM'} or set(data_types) == {'dem', 'DEM'}:
            return get_dem_temporal_interval()
        else:
            return get_unknow_temporal_interval()
