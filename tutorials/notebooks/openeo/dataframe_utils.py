
from temporal_utils import compute_temporal_extent
from spatial_utils import  get_latlon_bbox, create_utm_patch

import os
from typing import List
import geopandas as gpd
import rasterio
from shapely.geometry import Point
import pandas as pd
from typing import List, Dict

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
            "file_name": os.path.splitext(os.path.basename(file_path))[0],
            "geometry": utm_patch,  # Extract the geometry from the GeoDataFrame
            "crs": utm_crs.to_string(),
            "temporal_extent": temporal_extent
        }

def generate_geodataframe_per_utm(
    tif_files: List[str],
    start_date: str,
    nb_months: int,
    distance_m: float,
    resolution: float,
) -> List[gpd.GeoDataFrame]:
    """Generate a list of GeoDataFrames, one per unique CRS, with metadata and geometry for each .tif file."""
    
    # Dictionary to hold lists of GeoDataFrames per unique CRS
    crs_dict: Dict[str, List[gpd.GeoDataFrame]] = {}
    
    for file in tif_files:
        result = process_file(file, start_date, nb_months, distance_m, resolution)
        
        # Create a GeoDataFrame for each file with its original CRS
        file_gdf = gpd.GeoDataFrame([result], geometry="geometry", crs=result['crs'])
        
        # Use the CRS as a key in crs_dict
        crs_key = file_gdf.crs
        if crs_key not in crs_dict:
            crs_dict[crs_key] = []
        
        # Append the file-specific GeoDataFrame to the corresponding CRS list
        crs_dict[crs_key].append(file_gdf)
    
    # Create a list of concatenated GeoDataFrames, one per unique CRS
    geodataframes_per_crs = [
        gpd.GeoDataFrame(pd.concat(gdfs, ignore_index=True), crs=crs)
        for crs, gdfs in crs_dict.items()
    ]
    
    return geodataframes_per_crs

def split_jobs_per_utm(base_gdf: gpd.GeoDataFrame, max_points:int, grid_resolution:int = 3) -> List[gpd.GeoDataFrame]:
    """Append H3 index and split into smaller job dataframes."""
    original_crs = base_gdf.crs
    # Append H3 index, which will change the CRS temporarily
    base_gdf = append_h3_index(base_gdf, grid_resolution=grid_resolution)
    # Transform back to the original CRS
    h3_gdf = base_gdf.to_crs(original_crs)
    split_gdf = split_job_s2grid(h3_gdf, max_points=max_points)
    return split_gdf

def process_split_jobs(
    geodataframes: List[gpd.GeoDataFrame], max_points: int, grid_resolution: int = 3
) -> List[gpd.GeoDataFrame]:
    """Processes a list of GeoDataFrames by applying H3 indexing and splitting as needed."""
    
    all_splits = []
    
    # Loop over each GeoDataFrame in the list
    for gdf in geodataframes:
        # Apply prepare_split_jobs to each GeoDataFrame
        split_gdfs = split_jobs_per_utm(gdf, max_points=max_points, grid_resolution=grid_resolution)
        
        # Extend the all_splits list with the resulting split GeoDataFrames
        all_splits.extend(split_gdfs)
    
    return all_splits

#TODO evaluate need
def create_job_dataframe_s2(split_jobs: List[gpd.GeoDataFrame]) -> pd.DataFrame:
    """Create a DataFrame from split jobs with essential information for each job, including feature count."""
    job_data = []
    for job in split_jobs:

        temporal_extent = job.temporal_extent.iloc[0] if job.temporal_extent.iloc[0] else None
        s2_tile = job.tile.iloc[0] if job.tile.iloc[0] else None
        h3index = job.h3index.iloc[0] if job.h3index.iloc[0] else None
        crs = job.crs.to_string() if job.crs else None

        
        # Count the number of features in the GeoDataFrame (each row is a feature)
        feature_count = len(job)
        
        # Convert the GeoDataFrame to JSON
        job_json = job.to_json()

        # Append all information, including feature count
        job_data.append({
            'temporal_extent': temporal_extent,
            'geometry': job_json,
            's2_tile': s2_tile,
            'h3index': h3index,
            'crs': crs,
            'feature_count': feature_count  # Add the feature count here
        })

    return pd.DataFrame(job_data)



