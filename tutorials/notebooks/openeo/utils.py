
import os
import datetime
import rasterio
from pyproj import Transformer
from shapely.geometry import Point
import geopandas as gpd
from dateutil.relativedelta import relativedelta
from openeo_gfmap.manager.job_splitters import split_job_s2grid, append_h3_index
from typing import List, Dict


def create_temporal_extent(start_date_str: str, nb_months: int):
    """
    Create a temporal extent by adding months to the start date and adjusting for invalid dates.

    Args:
    start_date_str (str): The start date as a string in "YYYY-MM-DD" format.
    nb_months (int): The number of months to add.

    Returns:
    list: A list with the start date and end date as strings in "YYYY-MM-DD" format.
    """
    # Convert the start date string to a datetime object
    startdate = datetime.datetime.strptime(start_date_str, "%Y-%m-%d")

    # Add the number of months using relativedelta
    enddate = startdate + relativedelta(months=nb_months)

    # Convert the datetime objects back to strings
    return [startdate.strftime("%Y-%m-%d"), enddate.strftime("%Y-%m-%d")]

def get_tif_files(src_dir):
    """Get all .tif files from the directory and subdirectories."""
    return [os.path.join(root, file) 
            for root, _, files in os.walk(src_dir) 
            for file in files if file.endswith(".tif")]


def get_latlon_bbox(transform, crs, width, height):
    """Calculate bounding box in WGS84 for a given image."""
    corners_pixel = [(0, 0), (width, 0), (0, height), (width, height)]
    corners_native = [rasterio.transform.xy(transform, row, col, offset='center') for col, row in corners_pixel]

    if crs.to_string() != "EPSG:4326":
        transformer = Transformer.from_crs(crs, "EPSG:4326", always_xy=True)
        corners_latlon = [transformer.transform(x, y) for x, y in corners_native]
    else:
        corners_latlon = corners_native

    min_lon = min(c[0] for c in corners_latlon)
    max_lon = max(c[0] for c in corners_latlon)
    min_lat = min(c[1] for c in corners_latlon)
    max_lat = max(c[1] for c in corners_latlon)

    return {"west": min_lon, "south": min_lat, "east": max_lon, "north": max_lat, "crs": "EPSG:4326"}


# Function to create a UTM patch (64x64 m) around a geometry's centroid
def create_utm_patch(geometry, distance_m=320, resolution=20.0):
    """
    Buffer around centroid to create a 64x64 meter patch, aligned to the nearest grid defined by `resolution`.
    :param geometry: GeoDataFrame geometry in WGS84 CRS (lat/lon).
    :param distance_m: Half the patch size in meters (320 for a 64x64 patch).
    :param resolution: Resolution to snap centroid coordinates, in meters.
    :return: Buffered square patch and the UTM CRS.
    """
    # Estimate UTM CRS based on geometry
    utm_crs = geometry.estimate_utm_crs()
    geometry = geometry.to_crs(utm_crs)
    
    # Get the centroid and round to the specified resolution grid
    centroid = geometry.centroid
    adjusted_centroid = Point(
        round(centroid.x / resolution) * resolution,
        round(centroid.y / resolution) * resolution
    )
    
    # Create square buffer
    utm_patch = adjusted_centroid.buffer(distance_m, cap_style=3)
    return utm_patch, utm_crs

def compute_percentiles(base_features, percentiles=[0.1, 0.25, 0.50, 0.75, 0.9]):
    """
    Computes P10, P25, P50, P75, P90 without depending on metadata early.
    """

    # Inner function to compute quantiles
    def computeStats(input_timeseries):
        return input_timeseries.quantiles(percentiles)

    # Apply dimension to calculate statistics
    stats = base_features.apply_dimension(
        dimension='t', target_dimension="bands", process=computeStats
    )

    # Create dynamic band names only after statistics are computed
    band_names = base_features.metadata.band_names if base_features.metadata else []
    all_bands = [
        f"{band}_{stat}"
        for band in band_names
        for stat in ["P10", "P25", "P50", "P75", "P90"]
    ]
    return stats.rename_labels("bands", all_bands)



def process_file(file_path: str, start_date: str, nb_months: int) -> Dict:
    """
    Process a single .tif file to extract relevant metadata and geometry.

    Parameters:
    - file_path (str): Path to the .tif file.
    - start_date (str): Start date for temporal extent.
    - nb_months (int): Number of months to add to the start date for temporal extent.

    Returns:
    - Dict: Extracted file information including geometry, temporal extent, and file name.
    """
    with rasterio.open(file_path) as src:
        # File-specific properties
        file_transform = src.transform
        crs = src.crs
        width, height = src.width, src.height

        # Calculate bounding box in latitude and longitude
        bbox_latlon = get_latlon_bbox(file_transform, crs, width, height)
        center_point = Point(
            (bbox_latlon["west"] + bbox_latlon["east"]) / 2,
            (bbox_latlon["south"] + bbox_latlon["north"]) / 2
        )

        # Convert center point to a GeoDataFrame with EPSG_LATLON
        center_geom = gpd.GeoDataFrame(geometry=[center_point], crs=EPSG_LATLON)

        # Create UTM patch based on the center geometry
        utm_patch, utm_crs = create_utm_patch(center_geom, distance_m=DISTANCE_M, resolution=RESOLUTION)

        # Transform UTM patch to latitude/longitude
        transformer = Transformer.from_crs(utm_crs, EPSG_LATLON, always_xy=True)
        latlon_patch = transform(transformer.transform, utm_patch)

        # Create temporal extent
        temporal_extent = create_temporal_extent(start_date, nb_months)

        return {
            "file_name": file_path,
            "geometry": latlon_patch,  # Storing as Shapely geometry
            "temporal_extent": temporal_extent
        }


def generate_geodataframe_from_files(tif_files: List[str], start_date: str, nb_months: int) -> gpd.GeoDataFrame:
    """
    Process each .tif file to create a GeoDataFrame with metadata and geometry.

    Parameters:
    - tif_files (List[str]): List of .tif file paths.
    - start_date (str): Start date for temporal extent.
    - nb_months (int): Number of months to add to the start date for temporal extent.

    Returns:
    - gpd.GeoDataFrame: GeoDataFrame containing processed file information.
    """
    # Process each selected file and convert to a DataFrame
    data = [process_file(file, start_date, nb_months) for file in tif_files]
    return gpd.GeoDataFrame(data, geometry="geometry", crs=EPSG_LATLON)


def prepare_split_jobs(base_gdf: gpd.GeoDataFrame) -> List[gpd.GeoDataFrame]:
    """
    Append H3 index to the base GeoDataFrame and split into smaller job dataframes.

    Parameters:
    - base_gdf (gpd.GeoDataFrame): The base GeoDataFrame containing all processed files.

    Returns:
    - List[gpd.GeoDataFrame]: List of split GeoDataFrames ready for further processing.
    """
    # Append H3 index to base GeoDataFrame
    base_gdf = append_h3_index(base_gdf, grid_resolution=3)
    # Split jobs into separate GeoDataFrames with a max of 1 point each (for demonstration)
    return split_job_s2grid(base_gdf, max_points=1)


def create_job_dataframe_s2(split_jobs: List[gpd.GeoDataFrame]) -> pd.DataFrame:
    """
    Create a DataFrame from split jobs with essential information for each job.

    Parameters:
    - split_jobs (List[gpd.GeoDataFrame]): List of split GeoDataFrames.

    Returns:
    - pd.DataFrame: DataFrame containing job metadata for each split job.
    """
    job_data = []
    for job in split_jobs:
        # Extract the first row values for temporal extent, tile ID, and H3 index
        temporal_extent = job.temporal_extent.iloc[0]
        s2_tile = job.tile.iloc[0]
        h3index = job.h3index.iloc[0]
        geometry = job.geometry.to_json()  # Convert geometry to JSON format

        # Add job data to the list
        job_data.append({
            'temporal_extent': temporal_extent,
            'geometry': geometry,
            's2_tile': s2_tile,
            'h3index': h3index
        })

    return pd.DataFrame(job_data)

