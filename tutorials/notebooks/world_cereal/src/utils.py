"""
Utils for World cereal Q1 dataset
"""
import os
from datetime import datetime, timedelta
from glob import glob
from typing import List
import json
import pystac

import geopandas as gpd
import pandas as pd


XLSX_MEDIA_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


def curate_legend(
    df: pd.DataFrame, first_column: int, second_column: int
) -> pd.DataFrame:
    """
    Curate xls legend file to a dataframe

    Parameters
    ----------
    df : pd.DataFrame
        Dataframe with the xls legend file
    first_column : int
        First column to keep
    second_column : int
        Second column to keep

    Returns
    -------
    pd.DataFrame
        Curated dataframe
    """
    df = df.iloc[:, first_column:second_column]
    # Set first row as column names and remove first row
    df.columns = df.iloc[0]
    df = df.iloc[1:]
    # Remove empty rows
    df = df.dropna(how="all")

    return df


def get_files_extent(files: List[str], crs: str = "epsg:4326") -> List:
    """
    Get the bounding boxes of a list of shapefiles

    Parameters
    ----------
    files : List[str]
        List of files to get the extent
    crs : str, optional
        CRS of the shapefiles, by default "epsg:4326"

    Returns
    -------
    Dict[str, List[float]]
        Dictionary with the shapefile name as key and the bounding box as value
    """
    bboxes, datetimes = [], []
    for file in files:
        if file.endswith(".parquet"):
            gdf = gpd.read_parquet(file)
        else:
            gdf = gpd.read_file(file)
        gdf = gdf.to_crs(crs)
        bbox = list(gdf.total_bounds)
        bboxes.append(bbox)
        val_time = gdf["valtime"].unique()[0]
        val_time = datetime.strptime(val_time, "%Y-%m-%d")
        datetimes.append(val_time)

    spatial_extent = get_spatial_extent(bboxes)
    temporal_extent = get_temporal_extent(datetimes)

    return spatial_extent, temporal_extent


def get_spatial_extent(bboxes: List[str]) -> List[float]:
    """
    Get the bounding box of a list of shapefiles

    Parameters
    ----------
    files : List[str]
        List of files to get the extent
    crs : str, optional
        CRS of the shapefiles, by default "epsg:4326"

    Returns
    -------
    List[float]
        Bounding box of the shapefiles
    """
    bbox = [
        min([bbox[0] for bbox in bboxes]),
        min([bbox[1] for bbox in bboxes]),
        max([bbox[2] for bbox in bboxes]),
        max([bbox[3] for bbox in bboxes]),
    ]

    return bbox


def get_temporal_extent(datetimes: List[datetime]) -> List[datetime]:
    """
    Get the temporal extent of a list of dates

    Parameters
    ----------
    dates : List[datetime]
        List of dates to get the extent

    Returns
    -------
    List[datetime]
        Temporal extent of the dates
    """
    if len(datetimes) > 1:
        intervals = (min(datetimes), max(datetimes))
    elif len(datetimes) == 1:
        # Quit one day and add one day
        date = datetimes[0]
        intervals = (date - timedelta(days=1), date + timedelta(days=1))

    return intervals


def save_shapefiles_as_parquet(shapefiles: List[str], crs: str = "epsg:4326") -> None:
    """
    Save a list of shapefiles as parquet files

    Parameters
    ----------
    shapefiles : List[str]
        List of shapefiles
    output_dir : str
        Output directory
    crs : str, optional
        CRS of the shapefiles, by default "epsg:4326"
    """
    for file in shapefiles:
        output_dir = os.path.dirname(file)
        output_file = os.path.basename(file).replace(".shp", ".parquet")
        if os.path.exists(os.path.join(output_dir, output_file)):
            continue
        gdf = gpd.read_file(file)
        gdf = gdf.to_crs(crs)
        gdf.to_parquet(os.path.join(output_dir, output_file))

    parquet_files = glob(os.path.join(output_dir, "*.parquet"))
    return parquet_files


legends_dict = {
    "crop_type": pd.read_csv("legends/crop_type.csv"),
    "irrigation": pd.read_csv("legends/irrigation.csv"),
    "land_cover": pd.read_csv("legends/land_cover.csv"),
}


def get_property_value_from_dict(dict, value):
    legend_df = legends_dict[dict]
    name = legend_df.loc[legend_df["Final Values"] == value, "Name"]
    if not name.empty:
        return name.values[0]


def generate_stac_item(feature, collection) -> pystac.Item:
    """
    Generate a STAC item by a feature

    Parameters
    ----------
    feature
        Feature to generate the STAC item

    Returns
    -------
    pystac.Item
        STAC item
    """
    # Datetime
    val_time = feature["valtime"]
    val_time = datetime.strptime(val_time, "%Y-%m-%d")
    # Properties
    lc = get_property_value_from_dict("land_cover", feature["LC"])
    crop_type = get_property_value_from_dict("crop_type", feature["CT"])
    irrigation = get_property_value_from_dict("irrigation", feature["IRR"])
    properties = {
        "LC": {
            "value": feature["LC"],
            "name": lc,
        },
        "CT": {
            "value": feature["CT"],
            "name": crop_type,
        },
        "IRR": {
            "value": feature["IRR"],
            "name": irrigation,
        },
    }
    # Create item
    item = pystac.Item(
        id=feature["sampleID"],
        geometry=feature.geometry.__geo_interface__,
        bbox=feature.geometry.bounds,
        datetime=val_time,
        properties=properties,
        collection=collection,
    )

    return item
