
from temporal_utils import compute_temporal_extent
from spatial_utils import  get_latlon_bbox, create_utm_patch

import os
import random
from typing import List, Dict
import geopandas as gpd
import rasterio
from shapely.geometry import Point
from shapely.ops import transform
from pyproj import Transformer
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


def get_latlon_bbox(transform, crs, width, height) -> Dict[str, float]:
    """Calculate bounding box in WGS84 for a given image."""
    corners_pixel = [(0, 0), (width, 0), (0, height), (width, height)]
    corners_native = [rasterio.transform.xy(transform, row, col, offset='center') for col, row in corners_pixel]

    transformer = Transformer.from_crs(crs, "EPSG:4326", always_xy=True)
    corners_latlon = [transformer.transform(x, y) for x, y in corners_native]

    min_lon = min(c[0] for c in corners_latlon)
    max_lon = max(c[0] for c in corners_latlon)
    min_lat = min(c[1] for c in corners_latlon)
    max_lat = max(c[1] for c in corners_latlon)

    return {"west": min_lon, "south": min_lat, "east": max_lon, "north": max_lat, "crs": "EPSG:4326"}


def create_utm_patch(geometry, distance_m: float, resolution: float):
    """
    Create a UTM patch (square buffer) around a geometry's centroid.
    
    Args:
        geometry: GeoDataFrame geometry in WGS84 CRS (lat/lon).
        distance_m (float): Half the patch size in meters.
        resolution (float): Resolution to snap centroid coordinates, in meters.
    
    Returns:
        utm_patch: Buffered square patch.
        utm_crs: The UTM CRS for the geometry.
    """
    utm_crs = geometry.estimate_utm_crs()
    geometry = geometry.to_crs(utm_crs)
    
    centroid = geometry.centroid
    adjusted_centroid = Point(
        round(centroid.x / resolution) * resolution,
        round(centroid.y / resolution) * resolution
    )
    
    utm_patch = adjusted_centroid.buffer(distance_m, cap_style=3)
    return utm_patch, utm_crs


def process_file(file_path: str, start_date: str, nb_months: int, distance_m: float, resolution: float) -> Dict[str, object]:
    """Process a single .tif file to extract metadata and geometry."""
    with rasterio.open(file_path) as src:
        # Get bounding box and create a center point
        bbox_latlon = get_latlon_bbox(src.transform, src.crs, src.width, src.height)
        center_point = Point((bbox_latlon["west"] + bbox_latlon["east"]) / 2,
                             (bbox_latlon["south"] + bbox_latlon["north"]) / 2)

        center_geom = gpd.GeoDataFrame(geometry=[center_point], crs=src.crs)  # Use the CRS from the raster file
        utm_patch, _ = create_utm_patch(center_geom, distance_m, resolution)

        # Transform the geometry to lat/lon (EPSG:4326)
        transformer = Transformer.from_crs(center_geom.crs, "EPSG:4326", always_xy=True)
        latlon_patch = transform(transformer.transform, utm_patch)

        # Compute temporal extent
        temporal_extent = compute_temporal_extent(start_date, nb_months)

        # Ensure the latlon_patch is in EPSG:4326
        #latlon_patch_gdf = gpd.GeoDataFrame(geometry=[latlon_patch], crs=src.crs)
        #latlon_patch_gdf = latlon_patch_gdf.set_crs("EPSG:4326", allow_override=True)

        # Compute temporal extent (you should already have the function for that)
        temporal_extent = compute_temporal_extent(start_date, nb_months)

        return {
            "file_name": file_path,
            "geometry": latlon_patch,  # Extract the geometry from the GeoDataFrame
            "temporal_extent": temporal_extent
        }


def generate_geodataframe_from_files(tif_files: List[str], start_date: str, nb_months: int, distance_m: float, resolution: float) -> gpd.GeoDataFrame:
    """Generate a GeoDataFrame with metadata and geometry for each .tif file."""
    data = [process_file(file, start_date, nb_months, distance_m, resolution) for file in tif_files]
    return gpd.GeoDataFrame(data, geometry="geometry", crs="EPSG:4326")

#TODO evaluate need
def prepare_split_jobs(base_gdf: gpd.GeoDataFrame, max_points:int, grid_resolution:int = 3) -> List[gpd.GeoDataFrame]:
    """Append H3 index and split into smaller job dataframes."""
    base_gdf = append_h3_index(base_gdf, grid_resolution=grid_resolution)
    return split_job_s2grid(base_gdf, max_points=max_points)

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

    return base_df