
import rasterio
from pyproj import Transformer
from pyproj import Transformer
from shapely.geometry import Point


def get_latlon_bbox(transform, crs, width, height):
    """Calculate bounding box in WGS84 for a given image."""
    corners_pixel = [(0, 0), (width, 0), (0, height), (width, height)]
    corners_native = [rasterio.transform.xy(transform, row, col, offset='center') for col, row in corners_pixel]

    if crs != "EPSG:4326":
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
    geometry = geometry.to_crs(geometry.estimate_utm_crs())
    
    # Get the centroid and round to the specified resolution grid
    centroid = geometry.centroid
    adjusted_centroid = Point(
        round(centroid.x / resolution) * resolution,
        round(centroid.y / resolution) * resolution
    )
    
    # Create square buffer
    utm_patch = adjusted_centroid.buffer(distance_m, cap_style=3)
    return utm_patch, geometry.estimate_utm_crs()
