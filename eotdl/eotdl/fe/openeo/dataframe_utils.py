
from .temporal_utils import compute_temporal_extent
from .spatial_utils import  buffer_geometry

import os
from typing import List
import geopandas as gpd

import pandas as pd
from typing import List, Dict, Any

try:
    import openeo_gfmap
except ImportError:
    print("openeo_gfmap is not installed, please install it with 'pip install openeo_gfmap'")

from openeo_gfmap.manager.job_splitters import split_job_s2grid, append_h3_index

def create_utm_patch(
    row: Any,
    parent_crs: str,
    start_date: str,
    nb_months: int,
    pixel_size: int,
    resolution: int
) -> Dict[str, Any]:
    """
    Process a single row from a GeoDataFrame to extract metadata and buffer geometry.
    
    Parameters:
        row: A single row of a GeoDataFrame.
        start_date: Start date for the temporal extent (ISO format string).
        nb_months: Number of months for the temporal extent.
        buffer_distance: Buffer distance in meters for the geometry.
    
    Returns:
        A dictionary with metadata and processed geometry.
    """
    # Extract the polygon geometry from the row
    # Create a single-row GeoDataFrame
    gdf = gpd.GeoDataFrame(
        [row], 
        crs=parent_crs, 
        geometry="geometry"
    )
    
    buffer = int(pixel_size*resolution/2)
    # Apply the buffer_geometry function
    buffered_gdf = buffer_geometry(gdf, buffer=buffer, resolution = resolution)

    # Compute the temporal extent
    temporal_extent = compute_temporal_extent(start_date, nb_months)

    # Return the processed data
    return {
        "fid": row.get("fid"),  # Include any relevant identifier
        "geometry": buffered_gdf.iloc[0].geometry,
        "crs": buffered_gdf.crs.to_string(),
        "temporal_extent": temporal_extent,
    }

def process_patch_geodataframe(
    geodataframe: gpd.GeoDataFrame,
    start_date: str,
    nb_months: int,
    buffer_distance: int,
    resolution: int
) -> gpd.GeoDataFrame:
    """
    Process a GeoDataFrame to generate buffered geometries and metadata for each row.
    
    Parameters:
        geodataframe: The input GeoDataFrame with geometries to process.
        start_date: Start date for the temporal extent (ISO format string).
        nb_months: Number of months for the temporal extent.
        buffer_distance: Buffer distance in meters for the geometry.
        resolution: Spatial resolution for geometry rounding.
    
    Returns:
        A processed GeoDataFrame with buffered geometries and additional metadata.
    """
    results = []  # List to store processed rows
    
    for _, row in geodataframe.iterrows():
        # Process each row and collect the result
        result = create_utm_patch(row, geodataframe.crs, start_date, nb_months, buffer_distance, resolution)
        results.append(result)
    
    # Convert the list of results into a GeoDataFrame
    processed_gdf = gpd.GeoDataFrame(
        results, 
        geometry="geometry", 
        crs=result['crs']
    )
    
    return processed_gdf

def process_geodataframe(
    geodataframe: gpd.GeoDataFrame,
    start_date: str,
    nb_months: int,
    extra_cols: List[str] = [],

) -> gpd.GeoDataFrame:
    """
    Process a GeoDataFrame to generate buffered geometries and metadata for each row.
    
    Parameters:
        geodataframe: The input GeoDataFrame with geometries to process.
        start_date: Start date for the temporal extent (ISO format string).
        nb_months: Number of months for the temporal extent.
        buffer_distance: Buffer distance in meters for the geometry.
        resolution: Spatial resolution for geometry rounding.
    
    Returns:
        A processed GeoDataFrame with buffered geometries and additional metadata.
    """
    results = []  # List to store processed rows
    geodataframe = geodataframe.to_crs(epsg=4326)
    
    for _, row in geodataframe.iterrows():
    
        # Compute the temporal extent
        temporal_extent = compute_temporal_extent(start_date, nb_months)

        # Return the processed data
        result =  {
            # "fid": row.get("fid"),  # Include any relevant identifier
            "geometry": row.geometry,
            "crs": geodataframe.crs.to_string(),
            "temporal_extent": temporal_extent,
            **{col: row[col] for col in extra_cols}
        }  
        
        results.append(result)
    
    # Convert the list of results into a GeoDataFrame
    processed_gdf = gpd.GeoDataFrame(
        results, 
        geometry="geometry", 
        crs=result['crs']
    )
    
    return processed_gdf

def split_geodataframe_by_s2_grid(base_gdf: gpd.GeoDataFrame, max_points:int, grid_resolution:int = 3) -> List[gpd.GeoDataFrame]:
    """Append H3 index and split into smaller job dataframes."""
    original_crs = base_gdf.crs
    # Append H3 index, which will change the CRS temporarily
    base_gdf = append_h3_index(base_gdf, grid_resolution=grid_resolution)
    # Transform back to the original CRS
    h3_gdf = base_gdf.to_crs(original_crs)
    split_gdf = split_job_s2grid(h3_gdf, max_points=max_points)
    return split_gdf

#TODO evaluate need
def generate_featurecollection_dataframe(split_jobs: List[gpd.GeoDataFrame]) -> pd.DataFrame:
    """Create a DataFrame from split jobs with essential information for each job, including feature count."""
    job_data = []
    for job in split_jobs:

        # Ensure the temporal_extent field exists and handle missing data
        temporal_extent = job.temporal_extent.iloc[0] if 'temporal_extent' in job.columns and job.temporal_extent.iloc[0] else None
        
        # Handle missing S2 and H3 information gracefully
        s2_tile = job.tile.iloc[0] if 'tile' in job.columns and job.tile.iloc[0] else None
        h3index = job.h3index.iloc[0] if 'h3index' in job.columns and job.h3index.iloc[0] else None
        
        # Extract CRS as string
        crs = job.crs.to_string() if job.crs else None
        
        # Count the number of features (rows) in the GeoDataFrame
        feature_count = len(job)
        
        # Serialize the entire GeoDataFrame to GeoJSON (including geometry and attributes)
        job_json = job.to_json()

        # Append all information, including feature count
        job_data.append({
            'temporal_extent': temporal_extent,
            'geometry': job_json,  # The entire GeoDataFrame serialized to GeoJSON
            's2_tile': s2_tile,
            'h3index': h3index,
            'crs': crs,
            'feature_count': feature_count  # Include the feature count for the job
        })

    # Return the DataFrame with all job metadata
    return pd.DataFrame(job_data)


def process_and_create_advanced_patch_jobs(
    gdf: gpd.GeoDataFrame, 
    start_date: str, 
    nb_months: int, 
    pixel_size: int, 
    resolution: int, 
    max_points: int
) -> pd.DataFrame:
    """
    A wrapper function to process geospatial data and generate a job metadata DataFrame.
    
    Args:
        gdf (GeoDataFrame): The input GeoDataFrame with geometries.
        start_date (str): The start date for the temporal extent (ISO format).
        nb_months (int): Number of months for the temporal extent.
        buffer_distance (int): Buffer distance in meters for geometry.
        resolution (int): Spatial resolution for geometry rounding.
        max_points (int): Maximum number of points per job for splitting the grid.
    
    Returns:
        pd.DataFrame: A DataFrame containing the job metadata.
    """
    # Step 1: Process GeoDataFrame in which we create patches and temporal info
    processed_gdf = process_patch_geodataframe(
        gdf, start_date, nb_months, pixel_size, resolution
    )

    # Step 2: Split processed GeoDataFrame into smaller jobs by Sentinel-2 grid
    split_jobs = split_geodataframe_by_s2_grid(processed_gdf, max_points)

    # Step 3: Generate the job metadata DataFrame
    job_df = generate_featurecollection_dataframe(split_jobs)

    return job_df





