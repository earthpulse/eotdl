"""
Geo Utils
"""

import tarfile
from typing import Union
from statistics import mean

import geopandas as gpd
import rasterio
import rasterio.warp

from shapely import geometry
from shapely.geometry import box, Polygon, shape
from pyproj import Transformer
from sentinelhub import BBox, CRS, bbox_to_dimensions
from pandas import isna


def is_bounding_box(bbox: list) -> bool:
    """
    Check if the given bounding box is a bounding box and is valid
    """
    if not isinstance(bbox, (list, tuple)) or len(bbox) != 4:
        return False

    for value in bbox:
        if not isinstance(value, (int, float)):
            return False

    minx, miny, maxx, maxy = bbox
    if minx >= maxx or miny >= maxy:
        return False

    return True


def compute_image_size(bounding_box, parameters):
    """
    Compute the image size from the bounding box and the resolution
    """
    bbox = BBox(bbox=bounding_box, crs=CRS.WGS84)
    bbox_size = bbox_to_dimensions(bbox, resolution=parameters.RESOLUTION)

    return bbox, bbox_size


def get_image_bbox(raster: Union[tarfile.ExFileObject, str]):
    """
    Get the bounding box of a raster
    """
    with rasterio.open(raster) as src:
        bounds = src.bounds
        dst_crs = "EPSG:4326"
        left, bottom, right, top = rasterio.warp.transform_bounds(
            src.crs, dst_crs, *bounds
        )
        bbox = [left, bottom, right, top]
    return bbox


def get_image_resolution(raster: Union[tarfile.ExFileObject, str]):
    """
    Get the resolution of a raster
    """
    with rasterio.open(raster) as src:
        resolution = src.res
    return resolution


def bbox_to_coordinates(bounding_box: list) -> list:
    """
    Convert a bounding box to a list of polygon coordinates
    """
    polygon_coordinates = [
        (bounding_box[0], bounding_box[1]),  # bottom left
        (bounding_box[0], bounding_box[3]),  # top left
        (bounding_box[2], bounding_box[3]),  # top right
        (bounding_box[2], bounding_box[1]),  # bottom right
        (bounding_box[0], bounding_box[1]),  # back to bottom left
    ]

    return polygon_coordinates


def bbox_to_polygon(bounding_box: list) -> Polygon:
    """
    Convert a bounding box to a shapely polygon
    """
    polygon = box(bounding_box[0], bounding_box[1], bounding_box[2], bounding_box[3])

    return polygon


from_4326_transformer = Transformer.from_crs("EPSG:4326", "EPSG:3857")
from_3857_transformer = Transformer.from_crs("EPSG:3857", "EPSG:4326")


def bbox_from_centroid(
    x: Union[int, float],
    y: Union[int, float],
    pixel_size: Union[int, float],
    width: Union[int, float],
    height: Union[int, float],
) -> list:
    """
    Generate a bounding box from a centroid, pixel size and image dimensions.

    Params
    ------
    x: int or float
        x coordinate of the centroid
    y: int or float
        y coordinate of the centroid
    pixel_size: int or float
        pixel size in meters
    width: int or float
        width of the image in pixels
    height: int or float
        height of the image in pixels

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


def generate_bounding_box(geom: geometry.point.Point, differences: list) -> list:
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

    bbox = (
        lon - (long_diff / 2),
        lat - (lat_diff / 2),
        lon + (long_diff / 2),
        lat + (lat_diff / 2),
    )

    # Round the coordinates to 6 decimals
    bounding_box = [round(i, 6) for i in bbox]

    return bounding_box


def calculate_average_coordinates_distance(bounding_box_by_location: dict) -> list:
    """
    Calculate the mean distance between maximum and minixum longitude
    and latitude of the bounding boxes from the existing locations.
    This is intended to use these mean distance to generate the bounding
    boxes of the new locations given a centroid.

    :param bounding_box_by_location: dictionary with format
    location_id : bounding_box for the existing locations in
    the sen12floods dataset.
    :return mean_long_diff, mean_lat_diff: mean longitude
    and latitude difference in the bounding boxes
    """
    long_diff_list, lat_diff_list = [], []

    for bbox in bounding_box_by_location.values():
        long_diff = bbox[2] - bbox[0]
        long_diff_list.append(long_diff)
        lat_diff = bbox[3] - bbox[1]
        lat_diff_list.append(lat_diff)

    mean_long_diff = mean(long_diff_list)
    mean_lat_diff = mean(lat_diff_list)

    return mean_long_diff, mean_lat_diff


def generate_new_locations_bounding_boxes(
    gdf: gpd.GeoDataFrame, mean_differences: list, latest_id: int
) -> dict:
    """
    Generate the bounding box of every new location, using
    the mean difference between the maximum and minimum calculated
    longitude and latitude. This function also returns the time
    interval which we want to request from Sentinel Hub Services.

    :param gdf: GeoDataFrame wiht the new locations that
    are going to be added to the dataset
    :param mean_differences: list with the longitude
    and latitude mean differences, which are going to be used to generate
    the bounding boxes.
    :return: bbox_by_new_location: dict with format {<location_id>:
    {'bounding_box': list(), 'time_interval': list()}, ... }
    that contains the bounding box and time interval of the imagery for each location
    """
    bbox_by_new_location = {}

    for _, row in gdf.iterrows():
        new_location_id = str(latest_id + 1)
        time_interval = row["Began"].strftime("%Y-%m-%d"), row["Ended"].strftime(
            "%Y-%m-%d"
        )
        bbox = generate_bounding_box(row["geometry"], mean_differences)
        bbox_by_new_location[new_location_id] = {
            "bounding_box": bbox,
            "time_interval": time_interval,
        }
        latest_id += 1

    return bbox_by_new_location


def convert_df_geom_to_shape(row):
    """
    Convert the geometry of a dataframe row to a shapely shape
    """
    if not isna(row["geometry"]):
        geo = shape(row["geometry"])
        wkt = geo.wkt
    else:
        wkt = "POLYGON EMPTY"

    return wkt
