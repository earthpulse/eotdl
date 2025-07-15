import pandas as pd
import geopandas as gpd
import s2sphere
from typing import List
from geojson import Feature, FeatureCollection


def combine_to_featurecollections(
    split_jobs: list[gpd.GeoDataFrame],
    id_field: str = "s2sphere_cell_id",
    target_crs: str = "EPSG:4326"
) -> pd.DataFrame:
    """
    Convert a list of GeoDataFrame chunks into a DataFrame of job-ready rows.
    Each row has:
      - the chunk's S2 ID & level
      - feature_count
      - all original feature attributes (as a list of dicts)
      - a geojson.FeatureCollection of the chunk, in WGS84 (lat/lon) coordinates

    Parameters:
    - split_jobs: list of GeoDataFrames to combine
    - id_field: column name to use as the unique cell identifier
    - target_crs: CRS to which all chunks will be reprojected (default EPSG:4326)

    Returns:
    - A pandas DataFrame where each row represents one input chunk
    """
    records = []

    for job in split_jobs:
        # Reproject to target CRS if needed
        if job.crs and job.crs.to_string() != target_crs:
            job_wgs = job.to_crs(target_crs)
        else:
            job_wgs = job.copy()

        # grab id metadata and feature count
        cell_id    = job_wgs[id_field].iloc[0]
        feat_count = len(job_wgs)

        # build properties list (all columns except geometry)
        props = job_wgs[["fid", "EC_hcat_n"]].to_dict(orient="records")

        # build FeatureCollection with valid GeoJSON lat/lon geometries
        features = []
        for geom, prop in zip(job_wgs.geometry, props):
            features.append(
                Feature(geometry=geom.__geo_interface__, properties=prop)
            )
        fc = FeatureCollection(features)

        records.append({
            id_field:       cell_id,
            "feature_count": feat_count,
            "properties":     props,
            # embed a proper GeoJSON FeatureCollection
            "geometry":       fc
        })

    df = pd.DataFrame(records)
    return df


def split_s2sphere(
    gdf: gpd.GeoDataFrame, max_points=500, start_level=8
) -> List[gpd.GeoDataFrame]:
    """
    EXPERIMENTAL
    Split a GeoDataFrame into multiple groups based on the S2geometry cell ID of each geometry.

    S2geometry is a library that provides a way to index and query spatial data. This function splits
    the GeoDataFrame into groups based on the S2 cell ID of each geometry, based on it's centroid.

    If a cell contains more points than max_points, it will be recursively split into
    smaller cells until each cell contains at most max_points points.

    More information on S2geometry can be found at https://s2geometry.io/
    An overview of the S2 cell hierarchy can be found at https://s2geometry.io/resources/s2cell_statistics.html

    :param gdf: GeoDataFrame containing points to split
    :param max_points: Maximum number of points per group
    :param start_level: Starting S2 cell level
    :return: List of GeoDataFrames containing the split groups
    """

    if "geometry" not in gdf.columns:
        raise ValueError("The GeoDataFrame must contain a 'geometry' column.")

    if gdf.crs is None:
        raise ValueError("The GeoDataFrame must contain a CRS")

    # Store the original CRS of the GeoDataFrame and reproject to EPSG:3857
    original_crs = gdf.crs
    gdf = gdf.to_crs(epsg=3857)

    # Add a centroid column to the GeoDataFrame and convert it to EPSG:4326
    gdf["centroid"] = gdf.geometry.centroid

    # Reproject the GeoDataFrame to its orginial CRS
    gdf = gdf.to_crs(original_crs)

    # Set the GeoDataFrame's geometry to the centroid column and reproject to EPSG:4326
    gdf = gdf.set_geometry("centroid")
    gdf = gdf.to_crs(epsg=4326)

    # Create a dictionary to store points by their S2 cell ID
    cell_dict = {}

    # Iterate over each point in the GeoDataFrame
    for _, row in gdf.iterrows():
        # Get the S2 cell ID for the point at a given level
        cell_id = _get_s2cell_id(row.centroid, start_level)

        if cell_id not in cell_dict:
            cell_dict[cell_id] = []

        cell_dict[cell_id].append(row)

    result_groups = []

    # Function to recursively split cells if they contain more points than max_points
    def _split_s2cell(cell_id, points, current_level=start_level):
        if len(points) <= max_points:
            if len(points) > 0:
                points = gpd.GeoDataFrame(
                    points, crs=original_crs, geometry="geometry"
                ).drop(columns=["centroid"])
                points["s2sphere_cell_id"] = cell_id
                points["s2sphere_cell_level"] = current_level
                result_groups.append(gpd.GeoDataFrame(points))
        else:
            children = s2sphere.CellId(cell_id).children()
            child_cells = {child.id(): [] for child in children}

            for point in points:
                child_cell_id = _get_s2cell_id(point.centroid, current_level + 1)
                child_cells[child_cell_id].append(point)

            for child_cell_id, child_points in child_cells.items():
                _split_s2cell(child_cell_id, child_points, current_level + 1)

    # Split cells that contain more points than max_points
    for cell_id, points in cell_dict.items():
        _split_s2cell(cell_id, points)

    return result_groups


def _get_s2cell_id(point, level):
    lat, lon = point.y, point.x
    cell_id = s2sphere.CellId.from_lat_lng(
        s2sphere.LatLng.from_degrees(lat, lon)
    ).parent(level)
    return cell_id.id()
