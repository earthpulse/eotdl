"""
Module for the STAC dataframe
"""

import pandas as pd
import geopandas as gpd
import pystac
import json
from geomet import wkt
from os.path import join
from os import makedirs
from typing import Union, Optional

from math import isnan
from .utils import convert_df_geom_to_shape, get_all_children
from pathlib import Path


class STACDataFrame(gpd.GeoDataFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @classmethod
    def from_stac_file(self, stac_file: pystac.STACObject):
        """
        Create a STACDataFrame from a STAC file

        :param stac_file: STAC file
        """
        return read_stac(stac_file)

    def to_stac(self, path):
        """
        Create a STAC catalog and children from a STACDataFrame
        """
        df = self.copy()

        if "id" in df.columns and "stac_id" in df.columns:
            id_column = "stac_id"
            stac_id_exists = True
        else:
            id_column = "id"
            stac_id_exists = False

        # First, create the catalog and its folder, if exists
        catalog_df = df[df["type"] == "Catalog"]

        if catalog_df.empty:
            makedirs(path, exist_ok=True)
        else:
            for _, row in catalog_df.iterrows():
                root_output_folder = path + "/" + row[id_column]
                makedirs(root_output_folder, exist_ok=True)
                row_json = row.to_dict()

                # Curate the json row
                row_json = self.curate_json_row(row_json, stac_id_exists)

                with open(join(root_output_folder, f"catalog.json"), "w") as f:
                    json.dump(row_json, f)

        # Second, create the collections and their folders, if exist
        collections = dict()
        collections_df = df[df["type"] == "Collection"]
        for _, row in collections_df.iterrows():
            stac_output_folder = join(root_output_folder, row[id_column])
            collections[row[id_column]] = stac_output_folder
            makedirs(stac_output_folder, exist_ok=True)
            row_json = row.to_dict()

            # Curate the json row
            row_json = self.curate_json_row(row_json, stac_id_exists)

            with open(join(stac_output_folder, f"collection.json"), "w") as f:
                json.dump(row_json, f)

        # Then, create the items and their folders, if exist
        features_df = df[df["type"] == "Feature"]
        for _, row in features_df.iterrows():
            collection = row["collection"]
            stac_output_folder = join(collections[collection], row[id_column])

            # Convert the geometry from WKT back to geojson
            row["geometry"] = row["geometry"].wkt
            row["geometry"] = wkt.loads(row["geometry"])
            makedirs(stac_output_folder, exist_ok=True)
            row_json = row.to_dict()

            # Curate the json row
            row_json = self.curate_json_row(row_json, stac_id_exists)

            with open(join(stac_output_folder, f'{row_json["id"]}.json'), "w") as f:
                json.dump(row_json, f)

    def curate_json_row(self, row: dict, stac_id_exists: bool) -> dict:
        """
        Curate the json row of a STACDataFrame, in order to generate a valid STAC file

        :param row: row of a STACDataFrame
        :param stac_id_exists: if the stac_id column exists
        """
        keys_to_remove = list()

        # Remove the created_at and modified_at columns, if the STACDataFrame comes from GeoDB
        for i in "created_at", "modified_at":
            if i in row.keys():
                keys_to_remove.append(i)

        # Rename the stac_id column to id, to avoid conflicts with the id column
        if stac_id_exists:
            row["id"] = row["stac_id"]
            del row["stac_id"]

        # Remove the NaN values and empty strings
        for k, v in row.items():
            if (isinstance(v, float) and isnan(v)) or v == "" or not v:
                keys_to_remove.append(k)

        for key in keys_to_remove:
            if key in row.keys():
                del row[key]

        # Convert the value to dict if it is a string and is possible
        for k, v in row.items():
            if isinstance(v, str):
                try:
                    row[k] = json.loads(v)
                except json.decoder.JSONDecodeError:
                    pass

        return row

def read_stac(
    stac_file: Union[pystac.Catalog, pystac.Collection, str],
    geometry_column: Optional[str] = "geometry",
) -> STACDataFrame:
    """
    Read a STAC file and return a STACDataFrame

    :param stac_file: STAC file to read
    :param geometry_column: name of the geometry column
    """
    if isinstance(stac_file, str) or isinstance(stac_file, Path):
        stac_file = pystac.read_file(stac_file) # we assume this is always a catalog
    stac_file.make_all_asset_hrefs_absolute()
    children = get_all_children(stac_file)

    # Convert Dataframe to STACDataFrame
    dataframe = pd.DataFrame(children)
    dataframe[geometry_column] = dataframe.apply(convert_df_geom_to_shape, axis=1)
    stac_dataframe = STACDataFrame(
        dataframe,
        crs="EPSG:4326",
        geometry=gpd.GeoSeries.from_wkt(dataframe[geometry_column]),
    )

    return stac_dataframe
