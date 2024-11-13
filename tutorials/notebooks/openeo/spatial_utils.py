
import rasterio
from pyproj import Transformer, CRS
from shapely.geometry import Point, Polygon
import geopandas as gpd
from typing import List, Dict, Tuple



def compute_bbox_corners(transform: rasterio.Affine, width: int, height: int) -> List[Tuple[float, float]]:
    """Compute the corner coordinates of an image in its native CRS.

    Args:
        transform (rasterio.Affine): Affine transformation of the image.
        width (int): Image width in pixels.
        height (int): Image height in pixels.

    Returns:
        List[Tuple[float, float]]: List of corner coordinates (x, y) in the image's native CRS.
    """
    corners_pixel = [(0, 0), (width, 0), (0, height), (width, height)]
    return [rasterio.transform.xy(transform, row, col, offset='center') for col, row in corners_pixel]


def transform_corners_to_latlon(corners: List[Tuple[float, float]], crs: CRS) -> List[Tuple[float, float]]:
    """Transform coordinates from a given CRS to WGS84.

    Args:
        corners (List[Tuple[float, float]]): List of corner coordinates in the original CRS.
        crs (CRS): Coordinate reference system of the input coordinates.

    Returns:
        List[Tuple[float, float]]: List of transformed coordinates in WGS84.
    """
    if crs.to_string() == "EPSG:4326":
        return corners  # No transformation needed
    transformer = Transformer.from_crs(crs, "EPSG:4326", always_xy=True)
    return [transformer.transform(x, y) for x, y in corners]


def calculate_latlon_bbox(corners_latlon: List[Tuple[float, float]]) -> Dict[str, float]:
    """Calculate bounding box from a list of coordinates in WGS84.

    Args:
        corners_latlon (List[Tuple[float, float]]): Coordinates in WGS84.

    Returns:
        Dict[str, float]: Bounding box with 'west', 'south', 'east', 'north', and 'crs' as 'EPSG:4326'.
    """
    min_lon = min(c[0] for c in corners_latlon)
    max_lon = max(c[0] for c in corners_latlon)
    min_lat = min(c[1] for c in corners_latlon)
    max_lat = max(c[1] for c in corners_latlon)
    return {"west": min_lon, "south": min_lat, "east": max_lon, "north": max_lat, "crs": "EPSG:4326"}


def get_latlon_bbox(transform: rasterio.Affine, crs: CRS, width: int, height: int) -> Dict[str, float]:
    """Calculate bounding box in WGS84 for a given image.

    Args:
        transform (rasterio.Affine): Affine transformation of the image.
        crs (CRS): Coordinate reference system of the image.
        width (int): Width of the image.
        height (int): Height of the image.

    Returns:
        Dict[str, float]: Bounding box in WGS84.
    """
    corners_native = compute_bbox_corners(transform, width, height)
    corners_latlon = transform_corners_to_latlon(corners_native, crs)
    return calculate_latlon_bbox(corners_latlon)


def create_utm_patch(geometry: gpd.GeoDataFrame, distance_m: float, resolution: float) -> Tuple[Polygon, CRS]:
    """Create a square UTM patch centered on the geometry's centroid.

    Args:
        geometry (gpd.GeoDataFrame): GeoDataFrame with a single geometry in EPSG:4326 CRS.
        distance_m (float): Buffer distance in meters around the centroid.
        resolution (float): Grid resolution for snapping the centroid coordinates.

    Returns:
        Tuple[Polygon, CRS]: Buffered square patch as Polygon and its UTM CRS.
    """
    utm_crs = geometry.estimate_utm_crs()
    geometry_utm = geometry.to_crs(utm_crs)
    centroid = geometry_utm.geometry.centroid.iloc[0]

    # Snap centroid to the nearest grid point
    snapped_centroid = Point(
        round(centroid.x / resolution) * resolution,
        round(centroid.y / resolution) * resolution
    )
    utm_patch = snapped_centroid.buffer(distance_m, cap_style=3)
    return utm_patch, utm_crs
