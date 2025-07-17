import pandas as pd
import geopandas as gpd
import s2sphere
import pyproj
import logging
from shapely.errors import TopologicalError, GEOSException
from shapely.geometry.base import BaseGeometry
from typing import List, Optional, Dict, Any
from geojson import Feature, FeatureCollection


class FeatureCollectionBuilder:
    """
    Build GeoJSON FeatureCollections from GeoDataFrame groups,
    applying S2 splitting, buffering, and property extraction.
    """
    logger = logging.getLogger(__name__)
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(logging.INFO)

    def __init__(
        self,
        id_field: str = 's2_cell_id',
        target_crs: str = 'EPSG:4326',
        resolution: float = 10,
        property_fields: Optional[List[str]] = None,
        max_points: int = 500,
        start_level: int = 8
    ):
        self.id_field = id_field
        self.target_crs = target_crs
        self.half_res = resolution / 2
        self.property_fields = property_fields
        self.max_points = max_points
        self.start_level = start_level

    @staticmethod
    def repair_geometry(geom: BaseGeometry) -> BaseGeometry:
        try:
            return geom.buffer(0)
        except (ValueError, TopologicalError, GEOSException):
            return geom

    @staticmethod
    def determine_metric_crs(gdf: gpd.GeoDataFrame) -> pyproj.CRS:
        try:
            return gdf.estimate_utm_crs()
        except (RuntimeError, ValueError):
            return pyproj.CRS.from_epsg(3857)

    @staticmethod
    def reproject(gdf: gpd.GeoDataFrame, crs: Any) -> gpd.GeoDataFrame:
        if gdf.crs and gdf.crs.to_string() != str(crs):
            return gdf.to_crs(crs)
        return gdf

    @classmethod
    def safe_buffer(cls, geom: BaseGeometry, dist: float, **buffer_kwargs) -> Optional[BaseGeometry]:
        clean = cls.repair_geometry(geom)
        try:
            buf = clean.buffer(dist, **buffer_kwargs)
            if buf and not buf.is_empty:
                return buf
        except GEOSException:
            return None
        return clean

    @staticmethod
    def compute_s2_cell_id(point: BaseGeometry, level: int) -> int:
        lat, lon = point.y, point.x
        cell = s2sphere.CellId.from_lat_lng(
            s2sphere.LatLng.from_degrees(lat, lon)
        ).parent(level)
        return cell.id()

    def split_geodataframe_by_s2(
        self,
        gdf: gpd.GeoDataFrame
    ) -> List[gpd.GeoDataFrame]:
        if 'geometry' not in gdf or gdf.crs is None:
            raise ValueError("GeoDataFrame must have 'geometry' and CRS defined.")
        original_crs = gdf.crs
        centroids = (
            gdf.to_crs(epsg=3857)
               .assign(centroid=lambda df: df.geometry.centroid)
               .set_geometry('centroid')
               .to_crs(epsg=4326)
        )
        groups: Dict[int, List[pd.Series]] = {}
        for rec in centroids.itertuples(index=False):
            cid = self.compute_s2_cell_id(rec.centroid, self.start_level)
            groups.setdefault(cid, []).append(rec)
        partitions: List[gpd.GeoDataFrame] = []
        def subdivide(cell_id: int, records: List[pd.Series], level: int):
            if len(records) <= self.max_points:
                df = pd.DataFrame(records).drop(columns=['centroid'])
                df[self.id_field] = cell_id
                df['s2_cell_level'] = level
                partitions.append(
                    gpd.GeoDataFrame(df, crs=original_crs, geometry='geometry')
                )
            else:
                children = s2sphere.CellId(cell_id).children()
                child_map: Dict[int, List[pd.Series]] = {c.id(): [] for c in children}
                for rec in records:
                    cid2 = self.compute_s2_cell_id(rec.centroid, level + 1)
                    child_map.setdefault(cid2, []).append(rec)
                for cid2, recs in child_map.items():
                    if recs:
                        subdivide(cid2, recs, level + 1)
        for cid, recs in groups.items():
            subdivide(cid, recs, self.start_level)
        return partitions

    def _process_group(self, gdf: gpd.GeoDataFrame) -> Optional[Dict[str, Any]]:
        # Repair and drop invalid
        gdf = gdf.copy()
        gdf['geometry'] = gdf.geometry.map(self.repair_geometry)
        gdf = gdf[gdf.geometry.is_valid & ~gdf.geometry.is_empty & gdf.geometry.notna()]
        if gdf.empty:
            return None
        # Buffer
        metric_crs = self.determine_metric_crs(gdf)
        gdf = self.reproject(gdf, metric_crs)
        gdf['geometry'] = gdf.geometry.map(lambda geom: self.safe_buffer(geom, self.half_res))
        gdf = gdf[gdf.geometry.notna() & gdf.geometry.is_valid & ~gdf.geometry.is_empty]
        if gdf.empty:
            return None
        # Reproject back
        gdf = self.reproject(gdf, self.target_crs)
        gdf['geometry'] = gdf.geometry.map(self.repair_geometry)
        gdf = gdf[gdf.geometry.is_valid & ~gdf.geometry.is_empty & gdf.geometry.notna()]
        if gdf.empty:
            return None
        # Properties
        non_geom = [c for c in gdf.columns if c != gdf.geometry.name]
        first = non_geom[0]
        fields = [first] + [f for f in (self.property_fields or []) if f != first]
        props = gdf[fields].to_dict(orient='records')
        # Features
        features = [
            Feature(geometry=geom.__geo_interface__, properties=prop)
            for geom, prop in zip(gdf.geometry, props)
        ]
        return {
            self.id_field: int(gdf[self.id_field].iat[0]),
            'feature_count': len(gdf),
            'properties': props,
            'geometry': FeatureCollection(features)
        }

    def build(self, gdf_list: List[gpd.GeoDataFrame]) -> pd.DataFrame:
        total = sum(len(gdf) for gdf in gdf_list)
        all_parts: List[gpd.GeoDataFrame] = []
        for i, gdf in enumerate(gdf_list, 1):
            parts = self.split_geodataframe_by_s2(gdf)
            kept = [p for p in parts if not p.empty]
            self.logger.info(f"Input #{i}: split into {len(parts)} parts, kept {len(kept)}")
            all_parts.extend(kept)
        self.logger.info(f"Total partitions: {len(all_parts)}")
        records: List[Dict[str, Any]] = []
        skipped = 0
        for part in all_parts:
            rec = self._process_group(part)
            if rec is None:
                skipped += 1
            else:
                records.append(rec)
        self.logger.info(f"Generated {len(records)} records, skipped {skipped}")
        if not records:
            self.logger.warning("No valid records; returning empty DataFrame")
            return pd.DataFrame(columns=[self.id_field, 'feature_count', 'properties', 'geometry'])
        df = pd.DataFrame(records)
        self.logger.info(f"Final DataFrame: {len(df)} rows from {total} input features")
        return df