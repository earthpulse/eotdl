import geopandas as gpd
from shapely.geometry import Point

def buffer_geometry(gdf: gpd.GeoDataFrame, buffer: int, resolution: int) -> gpd.GeoDataFrame:
    """
    Buffer the geometries in a GeoDataFrame and return the modified GeoDataFrame.
    
    Parameters:
        gdf: Input GeoDataFrame with geometries to buffer.
        buffer: Buffer distance in meters.
    
    Returns:
        A GeoDataFrame with buffered geometries.
    """
    # Ensure the GeoDataFrame has a valid CRS
    if gdf.crs is None:
        raise ValueError("Input GeoDataFrame must have a defined CRS.")

    # Estimate the UTM CRS based on the data's centroid
    utm = gdf.estimate_utm_crs()
    gdf_utm = gdf.to_crs(utm)
    
    # Round the centroids to the nearest 20m grid and apply buffering
    gdf_utm['geometry'] = gdf_utm.centroid.apply(
        lambda point: Point(round(point.x / resolution) * resolution, round(point.y / resolution) * resolution)
    ).buffer(distance=buffer, cap_style=3)
    
    return gdf_utm
