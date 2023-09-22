"""
Module for data engineeringt
"""
from ..access.sentinelhub.client import SHClient
from ..access.sentinelhub.parameters import (sentinel_1_search_parameters, 
                                         sentinel_2_search_parameters)

import geopandas as gpd
import pandas as pd
import tarfile
import rasterio
import re
import datetime
import json

from shapely.geometry import box, Polygon
from pyproj import Transformer
from os.path import exists
from typing import Union, Optional, List


def get_images_by_location(gdf: gpd.GeoDataFrame) -> pd.DataFrame:
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
    uniques_location_id = gdf['location_id'].unique()   # List of unique location ids
    uniques_location_id.sort()

    images_count_list, images_dates_list = [], []

    # Iterate the unique location ids, count the number of images per location and generate
    # a list with the dates of every image in a location
    for location_id in uniques_location_id:
        dates = gdf[gdf['location_id'] == location_id]['datetime']
        images_count_list.append(dates.count())
        images_dates_list.append(dates.tolist())

    images_dates_list.sort()   # Sort the list of dates
    data = {'location_id': uniques_location_id, 'dates_count': images_count_list, 'dates_list': images_dates_list}
    df_dates_per_aoi = pd.DataFrame.from_dict(data)

    return df_dates_per_aoi


def generate_location_payload(gdf: Union[gpd.GeoDataFrame, pd.DataFrame], path: str) -> dict:
    """
    Generate a dictionary with the location payload of the locations in the GeoDataFrame, 
    such as the bounding box and the time interval to search for available data.
    """
    payload_cache = f"{path}/location_payload.json"
    if exists(payload_cache):
        # Read as dict
        with open(payload_cache, 'r') as f:
            payload = json.load(f)
        return payload
    
    bbox_date_by_location = dict()
    for i, row in gdf.iterrows():
        # Get list from dates_list column
        dates_list = list(row['dates_list'])
        for date in dates_list:
            location_id = row['location_id']
            date_formatted = datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%Y-%m-%d')
            location_id_formatted = f'{location_id}_{date_formatted}'
            bbox_date_by_location[location_id_formatted] = {
                'bounding_box': row['geometry'].bounds,
                # Convert str to datetime
                'time_interval': (date, date)
            }

    # Save to json
    with open(payload_cache, 'w') as f:
        json.dump(bbox_date_by_location, f)

    return bbox_date_by_location


sentinel_parameters = {'sentinel-1': sentinel_1_search_parameters,
                       'sentinel-2': sentinel_2_search_parameters}


def get_available_data_by_location(search_data: dict,
                                   eotdl_client: SHClient,
                                   sentinel_mission: str
                                   ) -> list:
    # TODO put in data access
    """
    Search and return a dict with the available Sentinel data for a dict with given locations and a time intervals.

    :param search_data: dictionary with the data required to search the available imagery in a given location
            and time interval. It must have the following format:
                {<location_id>: {'bounding_box': list(), 'time_interval': list()}, ... }
    :param eotdl_client: eotdl.SHClient object required to search for availabe data in Sentinel Hub 
    :param sentinel_mission: id of the required Sentinel mission. The value must be <sentinel-1> or <sentinel-2>
    :return: available_data: available data for downloading for a given location and time interval
    :return: not_available_data: list with the locations that does not have any available data for the
            given location and time interval
    """
    if sentinel_mission not in ('sentinel-1', 'sentinel-2'):
        print('The specified Sentinel mission is not valid. The values must be between <sentinel-1> and <sentinel-2>')
        return
    
    parameters = sentinel_parameters[sentinel_mission]

    available_data, not_available_data = dict(), list()
    for location_id, location_info in search_data.items():
        parameters.bounding_box = location_info['bounding_box']
        parameters.time_interval = location_info['time_interval']
        results = eotdl_client.search_available_sentinel_data(parameters)
        if results:
            # The returning results are composed by a list with format 
            # 'id': <image ID>, properties : {'datetime': <image date>}
            # As we can't make a bulk request with the ID but with the date time,
            # and we need all the available images in a time lapse and not
            # a mosaic, we are going to generate a dict with format
            # 'location_id': <location ID>,
            # {'bounding_box': <image bbox>, 'time_interval': <image date>}
            # This dictionary is digerible by the SHClient
            time_intervals = list()
            for result in results:
                datetime = result['properties']['datetime'][0:10]
                time_interval = (datetime, datetime)
                time_intervals.append(time_interval) if time_interval not in time_intervals else time_intervals
            available_data[location_id] = {'bounding_box': location_info['bounding_box'], 'time_interval': time_intervals}
        else:
            # We should have a trace with the locations without
            # available data
            not_available_data.append(location_id)

    return available_data, not_available_data


def get_tarfile_image_info(tar: str, Optional[path]: str = None, pattern: Optional[str] = r"\d{8}T\d{6}", level: Optional[int] = 2):
    """
    """
    if path:
        gdf_cache = f"{path}/tarfile_images_info.csv"
        if exists(gdf_cache):
            images_gdf = gpd.read_file(gdf_cache,
                                       GEOM_POSSIBLE_NAMES="geometry", 
                                       KEEP_GEOM_COLUMNS="NO")
            images_gdf.set_crs(epsg=4326, inplace=True)
            
            return images_gdf
    
    images_df = pd.DataFrame()
    with tarfile.open(tar, 'r:gz') as tar:
        rasters = [i for i in tar.getnames() if i.endswith(".tif") or i.endswith(".tiff")]
        for raster in rasters:
            r = tar.extractfile(raster)
            bbox = get_image_bbox(r)
            date = extract_image_date_in_folder(raster, pattern)
            date_formatted = datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%Y-%m-%d')
            id = extract_image_id_in_folder(raster, level)
            # Use pd.concat to append to dataframe
            images_df = pd.concat([images_df, pd.DataFrame({"location_id": [id], 
                                                            "datetime": [date], 
                                                            "bbox": [bbox]})])

    # Clean duplicates
    images_df = images_df.drop_duplicates(subset=["location_id", "datetime"])
    # Convert to geodataframe
    images_gdf = gpd.GeoDataFrame(images_df, 
                                  crs='EPSG:4326',
                                  geometry=images_df["bbox"].apply(lambda x: box(x[0], x[1], x[2], x[3])))
    # Drop bbox column
    images_gdf = images_gdf.drop(columns=["bbox"])
    # Set crs
    images_gdf = images_gdf.set_crs(epsg=4326)
    # Sort by location_id
    images_gdf = images_gdf.sort_values(by=["location_id"])
    if path:
        # Save to csv
        images_gdf.to_csv(gdf_cache, index=False)

    return images_gdf


def get_image_bbox(raster: Union[tarfile.ExFileObject, str]):
    with rasterio.open(raster) as src:
        bbox = src.bounds
    return bbox


def get_image_resolution(raster: Union[tarfile.ExFileObject, str]):
    with rasterio.open(raster) as src:
        resolution = src.res
    return resolution


def extract_image_date_in_folder(raster_path: str, pattern: str):
    case = re.findall(pattern, raster_path)

    if case:
        date = case[0]
        # Convert date to format YYYY-MM-DDT00:00:00.000Z as datetime object
        formatted_date = datetime.datetime.strptime(date, '%Y%m%dT%H%M%S').strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        return formatted_date
    
    return None


def extract_image_id_in_folder(raster_path: str, level: int):
    return raster_path.split("/")[level]


def get_first_last_dates(dataframe: Union[pd.DataFrame, gpd.GeoDataFrame], dates_column: Optional[str] = 'datetime'):
    """
    """
    dataframe[dates_column] = dataframe[dates_column].apply(lambda x: sorted(x))
    dataframe['first_date'] = dataframe['dates_list'].apply(lambda x: x[0])
    dataframe['last_date'] = dataframe['dates_list'].apply(lambda x: x[-1])
    dataframe = dataframe.sort_values(by=['first_date', 'last_date'])
    # Sort by sequence id
    dataframe = dataframe.sort_values(by=['location_id'])
    # Convert first_date and last_date to datetime, in format YYYY-MM-DD
    dataframe['first_date'] = pd.to_datetime(dataframe['first_date'], format='%Y-%m-%d')
    dataframe['last_date'] = pd.to_datetime(dataframe['last_date'], format='%Y-%m-%d')

    return dataframe


def create_time_slots(start_date: datetime.datetime, end_date: datetime.datetime, n_chunks: int):
    """
    """
    tdelta = (end_date - start_date) / n_chunks
    edges = [(start_date + i * tdelta).date().isoformat() for i in range(n_chunks)]
    slots = [(edges[i], edges[i + 1]) for i in range(len(edges) - 1)]

    return slots


def expand_time_interval(time_interval: Union[list, tuple], format: str='%Y-%m-%dT%H:%M:%S.%fZ') -> list:
    """
    """
    start_date = time_interval[0]
    end_date = time_interval[1]

    if isinstance(start_date, str):
        start_date = datetime.datetime.strptime(start_date, format)
    if isinstance(end_date, str):
        end_date = datetime.datetime.strptime(end_date, format)

    # Add one day to start date and remove one day to end date
    new_start_date = start_date - datetime.timedelta(days=1)
    new_end_date = end_date + datetime.timedelta(days=1)

    # Convert to string
    new_start_date = new_start_date.strftime(format)
    new_end_date = new_end_date.strftime(format)

    return new_start_date, new_end_date


def format_product_location_payload(location_payload: dict,
                                    images_response: dict,
                                    all_info: bool = False
                                    ) -> dict:
    """
    """
    for id, info in location_payload.items():
        # Add new key to the dictionary
        if all_info:
            location_payload[id]['image'] = images_response[id] if id in images_response else None
        else:
            location_payload[id]['image'] = images_response[id]['properties']['id'] if images_response[id] else None

    return location_payload


def bbox_to_coordinates(bounding_box: list) -> list:
    """
    """
    polygon_coordinates = [
        (bounding_box[0], bounding_box[1]),  # bottom left
        (bounding_box[0], bounding_box[3]),  # top left
        (bounding_box[2], bounding_box[3]),  # top right
        (bounding_box[2], bounding_box[1]),  # bottom right
        (bounding_box[0], bounding_box[1])   # back to bottom left
    ]

    return polygon_coordinates


def bbox_to_polygon(bounding_box: list) -> Polygon:
    """
    """
    polygon = box(bounding_box[0], bounding_box[1], bounding_box[2], bounding_box[3])

    return polygon


from_4326_transformer = Transformer.from_crs('EPSG:4326', 'EPSG:3857')
from_3857_transformer = Transformer.from_crs('EPSG:3857', 'EPSG:4326')


def bbox_from_centroid(x: Union[int, float], 
                       y: Union[int, float],
                       pixel_size: Union[int, float],
                       width: Union[int, float],
                       height: Union[int, float]
                       ) -> list:
    """
    Generate a bounding box from a centroid, pixel size and image dimensions.

    Params
    ------
    x: int|float
        x coordinate of the centroid
    y: int|float
        y coordinate of the centroid
    pixel_size: int|float
        pixel size of the image, in meters
    width: int|float
        image width, in pixels
    height: int|float
        image height, in pixels

    Returns
    -------
    bounding_box: list
        list with the bounding box coordinates
    """
    width_m = width * pixel_size
    heigth_m = height * pixel_size

    # Transform the centroid coordinates to meters
    centroid_m = from_4326_transformer.transform(x, y)

    # Calculate the bounding box coordinates
    min_x = centroid_m[0] - width_m / 2
    min_y = centroid_m[1] - heigth_m / 2
    max_x = centroid_m[0] + width_m / 2
    max_y = centroid_m[1] + heigth_m / 2

    # Convert the bounding box coordinates back to degrees
    min_x, min_y = from_3857_transformer.transform(min_x, min_y)
    max_x, max_y = from_3857_transformer.transform(max_x, max_y)

    return [min_y, min_x, max_y, max_x]
