import pandas as pd
import geopandas as gpd
import s2sphere
from typing import List, Optional, Dict, Any
from geojson import Feature, FeatureCollection


def split_geodataframe_by_s2(
    gdf: gpd.GeoDataFrame,
    max_points: int = 500,
    start_level: int = 8
) -> List[gpd.GeoDataFrame]:
    """
    Splits a GeoDataFrame into smaller GeoDataFrames based on S2 cell IDs.

    Each resulting GeoDataFrame contains at most `max_points` geometries,
    and includes columns for S2 cell ID and level.

    :param gdf: Input GeoDataFrame with point geometries and a defined CRS.
    :param max_points: Maximum number of points per output group.
    :param start_level: S2 cell level to start splitting.
    :return: List of GeoDataFrames partitioned by S2 cells.
    """
    if 'geometry' not in gdf:
        raise ValueError("GeoDataFrame must have a 'geometry' column.")
    if gdf.crs is None:
        raise ValueError("GeoDataFrame must have a defined CRS.")

    original_crs = gdf.crs
    # Convert to metric for accurate centroid calculation
    gdf_metric = gdf.to_crs(epsg=3857)
    gdf_metric['centroid'] = gdf_metric.geometry.centroid

    # Ensure centroids are in WGS84 for S2
    centroids_wgs84 = gdf_metric.set_geometry('centroid').to_crs(epsg=4326)

    # Assign initial S2 cell IDs
    cell_groups: Dict[int, List[pd.Series]] = {}
    for record in centroids_wgs84.itertuples(index=False):
        cell_id = _compute_s2_cell_id(record.centroid, level=start_level)
        cell_groups.setdefault(cell_id, []).append(record)

    partitions: List[gpd.GeoDataFrame] = []

    def _recurse_split(cell_id: int, records: List[pd.Series], level: int) -> None:
        if len(records) <= max_points:
            df = pd.DataFrame(records)
            df.drop(columns=['centroid'], inplace=True)
            df['s2_cell_id'] = cell_id
            df['s2_cell_level'] = level
            partitions.append(gpd.GeoDataFrame(df, crs=original_crs, geometry='geometry'))
            return

        children = s2sphere.CellId(cell_id).children()
        child_groups: Dict[int, List[pd.Series]] = {child.id(): [] for child in children}
        for rec in records:
            child_id = _compute_s2_cell_id(rec.centroid, level=level + 1)
            child_groups.setdefault(child_id, []).append(rec)
        for cid, recs in child_groups.items():
            if recs:
                _recurse_split(cid, recs, level + 1)

    for cid, recs in cell_groups.items():
        _recurse_split(cid, recs, start_level)

    return partitions


def build_feature_collections(
    groups: List[gpd.GeoDataFrame],
    id_field: str = 's2_cell_id',
    resolution: int = 10,
    property_fields: Optional[List[str]] = None
) -> pd.DataFrame:
    """
    Converts groups of GeoDataFrames into a pandas DataFrame with GeoJSON FeatureCollections.

    Each row includes the cell ID, feature count, properties list, and the GeoJSON geometry.

    :param groups: List of GeoDataFrames with a cell ID column.
    :param id_field: Column name for unique cell identifiers.
    :param target_crs: CRS for output geometries (default WGS84).
    :param property_fields: Specific additional columns to include in properties; the first non-geometry column is always included.
    :return: DataFrame with columns [id_field, feature_count, properties, geometry].
    """
    records: List[Dict[str, Any]] = []
    target_crs = 'EPSG:4326' # gejson requires WGS84

    for gdf in groups:

        # Step 1: Ensure we're in a projected CRS
        if gdf.crs.is_geographic:
            # Reproject to a metric CRS
            gdf = gdf.to_crs(epsg=3857)  

        # Step 2: Apply buffer in meters
        gdf.geometry = gdf.geometry.buffer(resolution / 2)

        # Step 3: Reproject to latlon CRS 
        gdf = gdf.to_crs(target_crs)

        #Step 4. Determine the first non-geometry column to always include
        cols = list(gdf.columns)
        geom_col = gdf.geometry.name
        first_field = next(col for col in cols if col != geom_col)

        # Build property DataFrame
        if property_fields is None:
            props_df = gdf.drop(columns=[geom_col])
        else:
            # Always include first_field plus any additional property_fields
            fields = [first_field] + [f for f in property_fields if f != first_field]
            props_df = gdf[fields]

        properties = props_df.to_dict(orient='records')
        cell_id = int(gdf[id_field].iat[0])
        count = len(gdf)

        # Build GeoJSON features
        features = [
            Feature(geometry=geom.__geo_interface__, properties=prop)
            for geom, prop in zip(gdf.geometry, properties)
        ]
        collection = FeatureCollection(features)

        records.append({
            id_field: cell_id,
            'feature_count': count,
            'properties': properties,
            'geometry': collection
        })

    return pd.DataFrame(records)


def _compute_s2_cell_id(
    point: Any,
    level: int
) -> int:
    """
    Computes the S2 cell ID for a shapely Point in WGS84.

    :param point: Shapely Point geometry with .x/.y in degrees.
    :param level: S2 cell level.
    :return: Integer S2 cell ID.
    """
    lat, lon = point.y, point.x
    cell = s2sphere.CellId.from_lat_lng(
        s2sphere.LatLng.from_degrees(lat, lon)
    ).parent(level)
    return cell.id()