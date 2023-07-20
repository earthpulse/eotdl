"""
Module for data engineeringt
"""
from ..access.sentinelhub.client import SHClient
from ..access.sentinelhub.utils import (sentinel_1_search_parameters, 
                                         sentinel_2_search_parameters)

import geopandas as gpd
import pandas as pd
import tarfile
import rasterio
import re
from shapely.geometry import box
import datetime


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
    uniques_location_id = gdf['location_id'].unique()   # List of unique location ids
    uniques_location_id.sort()

    images_count_list, images_dates_list = [], []

    # Iterate the unique location ids, count the number of images per location and generate
    # a list with the dates of every image in a location
    for location_id in uniques_location_id:
        dates = gdf[gdf['location_id'] == location_id]['datetime']
        images_count_list.append(dates.count())
        images_dates_list.append(dates.tolist())

    data = {'location_id': uniques_location_id, 'dates_count': images_count_list, 'dates_list': images_dates_list, 'geometry': [None] * len(uniques_location_id)}
    gdf_dates_per_aoi = gpd.GeoDataFrame.from_dict(data)

    # Set the geometry of the GeoDataFrame as the bounding box of the location
    gdf_dates_per_aoi['geometry'] = gdf_dates_per_aoi['location_id'].apply(lambda x: gdf[gdf['location_id'] == x]['geometry'].iloc[0])

    return gdf_dates_per_aoi


sentinel_parameters = {'sentinel-1': sentinel_1_search_parameters,
                       'sentinel-2': sentinel_2_search_parameters}


def get_available_data_by_location(search_data: dict,
                                   eotdl_client: SHClient,
                                   sentinel_mission: str
                                   ) -> list:
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


def get_tarfile_image_info(tar, pattern: str = r"\d{8}T\d{6}", level: int = 2):
    images_df = pd.DataFrame()
    with tarfile.open(tar, 'r:gz') as tar:
        rasters = [i for i in tar.getnames() if i.endswith(".tif") or i.endswith(".tiff")]
        for raster in rasters:
            r = tar.extractfile(raster)
            bbox = get_image_bbox(r)
            date = extract_image_date_in_folder(raster, pattern)
            id = extract_image_id_in_folder(raster, level)
            # Use pd.concat to append to dataframe
            images_df = pd.concat([images_df, pd.DataFrame({"location_id": [id], "datetime": [date], "bbox": [bbox]})])

    # Clean duplicates
    images_df = images_df.drop_duplicates(subset=["location_id", "datetime"])
    # Convert to geodataframe
    images_gdf = gpd.GeoDataFrame(images_df, geometry=images_df["bbox"].apply(lambda x: box(x[0], x[1], x[2], x[3])))
    # Drop bbox column
    images_gdf = images_gdf.drop(columns=["bbox"])
    # Set crs
    images_gdf = images_gdf.set_crs(epsg=4326)

    return images_gdf


def get_image_bbox(raster: tarfile.ExFileObject|str):
    with rasterio.open(raster) as src:
        bbox = src.bounds
    return bbox


def extract_image_date_in_folder(raster_path: str, pattern: str):
    case = re.findall(pattern, raster_path)

    if case:
        date = case[0]
        formatted_date = f"{date[:4]}-{date[4:6]}-{date[6:8]}T00:00:00.000Z"
        return formatted_date
    
    return None


def extract_image_id_in_folder(raster_path: str, level: int):
    return raster_path.split("/")[level]


def get_first_last_dates(dataframe: pd.DataFrame | gpd.GeoDataFrame, dates_column: str = 'datetime'):
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
