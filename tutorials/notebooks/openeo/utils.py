
import os
import datetime
import rasterio
from pyproj import Transformer
from shapely.geometry import Point
import geopandas as gpd
from dateutil.relativedelta import relativedelta


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




