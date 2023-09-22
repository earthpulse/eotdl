"""
Module for data engineering in the sen12floods dataset
"""
from ...access.sentinelhub.client import SHClient
from ...access.sentinelhub.parameters import (sentinel_1_search_parameters, 
                                         sentinel_2_search_parameters)
from statistics import mean

import geopandas as gpd
from shapely import geometry


def get_images_by_location(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """
    Generate a GeoDataFrame with the available images for each location in the dataset. 

    :param gdf: GeoDataFrame generated from the ItemCollection of a sen12floods collection
    :return gdf_dates_per_aoi:  GeoDataFrame with the available images for each location in
                                the dataset.
            The returned GeoDataFrame has three columns:
                - location_id: the unique ID of each location.
                - images_count: the count of available images of each location.
                - images_dates: list with the dates of the available images of each location.
    """
    uniques_location_id = gdf['scene_id'].unique()   # List of unique location ids
    uniques_location_id.sort()

    images_count_list, images_dates_list = [], []

    # Iterate the unique location ids, count the number of images per location and generate
    # a list with the dates of every image in a location
    for location_id in uniques_location_id:
        dates = gdf[gdf['scene_id'] == location_id]['datetime']
        images_count_list.append(dates.count())
        images_dates_list.append(dates.tolist())

    data = {'scene_id': uniques_location_id, 'dates_count': images_count_list, 'dates_list': images_dates_list}
    gdf_dates_per_aoi = gpd.GeoDataFrame.from_dict(data)

    return gdf_dates_per_aoi


def calculate_average_coordinates_distance(bounding_box_by_location: dict) -> list:
    """
    Calculate the mean distance between maximum and minixum longitude and latitude of the bounding boxes
    from the existing locations. This is intended to use these mean distance to generate the bounding 
    boxes of the new locations given a centroid.

    :param bounding_box_by_location: dictionary with format location_id : bounding_box for the existing
            locations in the sen12floods dataset.
    :return mean_long_diff, mean_lat_diff: mean longitude and latitude difference in the bounding boxes
    """
    long_diff_list, lat_diff_list = list(), list()

    for bbox in bounding_box_by_location.values():
        long_diff = bbox[2] - bbox[0]
        long_diff_list.append(long_diff)
        lat_diff = bbox[3] - bbox[1]
        lat_diff_list.append(lat_diff)

    mean_long_diff = mean(long_diff_list)
    mean_lat_diff = mean(lat_diff_list)

    return mean_long_diff, mean_lat_diff

def generate_bounding_box(geom: geometry.point.Point, 
                          differences: list
                          ) -> list:
    """
    Generate the bounding box of a given point using the difference
    between the maximum and mininum coordinates of the bounding box

    :param geom: shapely geometry object of the point which we want to
                generate the bounding box.
    :param differences: list with the difference between the maximum
                and minimum longitude and latitude coordinates.
    :return: list with the resulting bounding box from the computing.
    """
    long_diff, lat_diff = differences[0], differences[1]
    lon, lat = geom.x, geom.y
    
    bbox = (lon - (long_diff/2), 
            lat - (lat_diff/2), 
            lon + (long_diff/2), 
            lat + (lat_diff/2))
    
    # Round the coordinates to 6 decimals
    bounding_box = [round(i, 6) for i in bbox]

    return bounding_box


def generate_new_locations_bounding_boxes(gdf: gpd.GeoDataFrame,
                                          mean_differences: list,
                                          latest_id: int
                                          ) -> dict:
    """
    Generate the bounding box of every new location, using the mean difference between the maximum and
    minimum calculated longitude and latitude. This function also returns the time interval which we
    want to request from Sentinel Hub Services.

    :param gdf: GeoDataFrame wiht the new locations that are going to be added to the dataset
    :param mean_differences: list with the longitude and latitude mean differences, which are going to be used
            to generate the bounding boxes.
    :return: bbox_by_new_location: dict with format {<location_id>: {'bounding_box': list(), 'time_interval': list()}, ... }
            that contains the bounding box and time interval of the imagery for each location
    """
    bbox_by_new_location = dict()

    for i, row in gdf.iterrows():
        new_location_id = str(latest_id + 1)
        time_interval = row['Began'].strftime("%Y-%m-%d"), row['Ended'].strftime("%Y-%m-%d")
        bbox = generate_bounding_box(row['geometry'], mean_differences)
        bbox_by_new_location[new_location_id] = {'bounding_box': bbox, 'time_interval': time_interval}
        latest_id += 1

    return bbox_by_new_location
