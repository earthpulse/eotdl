
from temporal_utils import compute_temporal_extent
from spatial_utils import  get_latlon_bbox, create_utm_patch

import json
import os
import random
from typing import List
import geopandas as gpd
import rasterio
from shapely.geometry import Point
import pandas as pd
from openeo_gfmap.manager.job_splitters import split_job_s2grid, append_h3_index


def get_tif_files(directory: str) -> List[str]:
    """
    Retrieve all .tif files from a specified directory and its subdirectories.

    Args:
        directory (str): The directory to search for .tif files.

    Returns:
        List[str]: A list of file paths to the .tif files in the directory and its subdirectories.
    """
    tif_files = []
    for root, dirs, files in os.walk(directory):  # os.walk traverses all subdirectories
        for file in files:
            if file.lower().endswith('.tif'):
                tif_files.append(os.path.join(root, file))  # Add full file path
    return tif_files



def process_file(file_path: str, start_date: str, nb_months: int, distance_m: float, resolution: float) -> dict:
    """Process a single .tif file to extract metadata and geometry."""
    
    with rasterio.open(file_path) as src:
        file_transform = src.transform
        crs = src.crs
        width, height = src.width, src.height

        bbox_latlon = get_latlon_bbox(file_transform, crs, width, height)

        center_point = Point((bbox_latlon["west"] + bbox_latlon["east"]) / 2, 
                             (bbox_latlon["south"] + bbox_latlon["north"]) / 2)
        center_geom = gpd.GeoDataFrame(geometry=[center_point], crs="EPSG:4326")

        utm_patch, utm_crs = create_utm_patch(center_geom, distance_m=distance_m, resolution=resolution)
        #transformer = Transformer.from_crs(utm_crs, "EPSG:4326", always_xy=True)
        #latlon_patch = transform(transformer.transform, utm_patch)

        temporal_extent = compute_temporal_extent(start_date, nb_months)
        
        return {
            "file_name": file_path,
            "geometry": utm_patch,  # Extract the geometry from the GeoDataFrame
            "crs": crs,
            "temporal_extent": temporal_extent
        }

def generate_geodataframe_from_files(tif_files: List[str], start_date: str, nb_months: int, distance_m: float, resolution: float) -> gpd.GeoDataFrame:
    """Generate a GeoDataFrame with metadata and geometry for each .tif file."""
    
    data = []
    
    for file in tif_files:
        result = process_file(file, start_date, nb_months, distance_m, resolution)
        
        # Convert the result dictionary into a GeoDataFrame
        # Wrap the geometry into a GeoDataFrame with the correct CRS
        file_gdf = gpd.GeoDataFrame([result], geometry="geometry", crs=result['crs'])
        
        # Append the file_gdf to the list
        data.append(file_gdf)
    
    # Concatenate all the GeoDataFrames into one final GeoDataFrame
    final_gdf = gpd.GeoDataFrame(pd.concat(data, ignore_index=True))
    final_gdf.set_crs(crs=result['crs'])
    
    return final_gdf

def prepare_split_jobs(base_gdf: gpd.GeoDataFrame, max_points:int, grid_resolution:int = 3) -> List[gpd.GeoDataFrame]:
    """Append H3 index and split into smaller job dataframes."""
    original_crs = base_gdf.crs
    # Append H3 index, which will change the CRS temporarily
    base_gdf = append_h3_index(base_gdf, grid_resolution=grid_resolution)
    # Transform back to the original CRS
    h3_gdf = base_gdf.to_crs(original_crs)

    split_gdf = split_job_s2grid(h3_gdf, max_points=max_points)
    return split_gdf

#TODO evaluate need
def create_job_dataframe_s2(split_jobs: List[gpd.GeoDataFrame]) -> pd.DataFrame:
    """Create a DataFrame from split jobs with essential information for each job."""
    job_data = []
    for job in split_jobs:
        temporal_extent = job.temporal_extent.iloc[0]
        s2_tile = job.tile.iloc[0]
        h3index = job.h3index.iloc[0]
        geometry = job.geometry.to_json()

        job_data.append({
            'temporal_extent': temporal_extent,
            'geometry': geometry,
            's2_tile': s2_tile,
            'h3index': h3index
        })

    return pd.DataFrame(job_data)


def create_job_dataframe_from_tif_files(
    src_dir: str,
    num_files: int,
    start_date: str,
    nb_months: int,
    distance_m: float = 320.0,
    resolution: float = 20.0,
    max_points: int = 1
) -> pd.DataFrame:
    """Full pipeline to process .tif files and generate a job DataFrame."""
    tif_files = get_tif_files(src_dir)
    selected_files = random.sample(tif_files, num_files)

    base_df = generate_geodataframe_from_files(selected_files, start_date, nb_months, distance_m, resolution)
    split_df = prepare_split_jobs(base_df, max_points)
    job_df = create_job_dataframe_s2(split_df)

    return job_df

def create_geodataframe(job_df: pd.DataFrame, geometry_col: str = 'geometry') -> gpd.GeoDataFrame:
    """
    Convert a DataFrame with JSON geometries to a GeoDataFrame with the appropriate CRS.

    Parameters:
        job_df (pd.DataFrame): DataFrame containing a column with JSON-encoded geometries.
        geometry_col (str): The column name that contains the JSON geometry data.

    Returns:
        gpd.GeoDataFrame: GeoDataFrame with geometries and CRS set based on the input data.
    """
    # Parse the JSON in the specified geometry column to extract features
    features_list = [
        json.loads(geojson_str)['features'][0]  # Extracts the first feature from each FeatureCollection
        for geojson_str in job_df[geometry_col]
    ]
    
    # Attempt to extract CRS from the first geometry entry in the DataFrame
    crs_info = json.loads(job_df[geometry_col].iloc[0]).get("crs", {}).get("properties", {}).get("name")
    
    if not crs_info:
        raise ValueError("CRS information is missing in the input geometry data.")
    
    # Create the GeoDataFrame from the extracted features and set the CRS
    gdf = gpd.GeoDataFrame.from_features(features_list)
    gdf = gdf.set_crs(crs_info)  # Automatically set the CRS from the JSON metadata
    
    return gdf