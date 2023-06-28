"""
Module for the STAC dataframe
"""

import pandas as pd
import geopandas as gpd
import pystac
import json
import os
from xcube_geodb.core.geodb import GeoDBClient
from geomet import wkt
from os.path import join
from os import makedirs

from math import isnan
from .utils import convert_df_geom_to_shape, get_all_children


class STACDataFrame(gpd.GeoDataFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @classmethod
    def from_stac_file(self, stac_file):
        """
        Create a STACDataFrame from a STAC file
        """
        return read_stac(stac_file)

    @classmethod
    def from_geodb(
        self,
        server_url: str,
        server_port: int | str,
        client_id: str,
        client_secret: str,
        auth_aud: str,
        collection: str,
        database: str = None,
    ):
        """
        Create a STACDataFrame from a GeoDB collection

        :param server_url: GeoDB server url
        :param server_port: GeoDB server port
        :param client_id: GeoDB client id
        :param client_secret: GeoDB client secret
        :param auth_aud: GeoDB auth aud
        :param collection: GeoDB collection
        :param database: GeoDB database
        """
        geodb_client = GeoDBClient(
            server_url=server_url,
            server_port=server_port,
            client_id=client_id,
            client_secret=client_secret,
            auth_aud=auth_aud,
        )

        data = geodb_client.get_collection(collection, database=database)

        return STACDataFrame(data, crs="EPSG:4326")

    def ingest(
        self,
        collection: str,
        server_url: str = os.environ["SERVER_URL"],
        server_port: int = os.environ["SERVER_PORT"],
        client_id: str = os.environ["CLIENT_ID"],
        client_secret: str = os.environ["CLIENT_SECRET"],
        auth_aud: str = os.environ["AUTH_DOMAIN"],
        database: str = None,
    ):
        """
        Create a GeoDB collection from a STACDataFrame

        :param collection: dataset name (GeoDB collection)
        :param server_url: GeoDB server url
        :param server_port: GeoDB server port
        :param client_id: GeoDB client id
        :param client_secret: GeoDB client secret
        :param auth_aud: GeoDB auth aud
        :param database: GeoDB database
        """

        geodb_client = GeoDBClient(
            server_url=server_url,
            server_port=server_port,
            client_id=client_id,
            client_secret=client_secret,
            auth_aud=auth_aud,
        )

        # TODO: check name is unique (use eotdl-cli)

        # TODO: ingest assets (only if local)
        # TODO: rename assets in the dataframe with URLs (only if local)

        # ingest to geodb

        # Check if the collection already exists
        if geodb_client.collection_exists(collection, database=database):
            # geodb_client.drop_collection(collection, database=database)
            raise Exception(f"Collection {collection} already exists")

        # Rename the column id to stac_id, to avoid conflicts with the id column
        self.rename(columns={"id": "stac_id"}, inplace=True)
        # Fill the NaN with '' to avoid errors, except in the geometry column
        copy = self.copy()
        columns_to_fill = copy.columns.drop("geometry")
        self[columns_to_fill] = self[columns_to_fill].fillna("")

        # Create the collection if it does not exist
        # and insert the data
        collections = {collection: self._create_collection_structure(self.columns)}
        geodb_client.create_collections(collections, database=database)

        geodb_client.insert_into_collection(collection, database=database, values=self)

        # TODO: save data in eotdl

    def _create_collection_structure(self, columns: list) -> dict:
        """
        Create the schema structure of a GeoDB collection from a STACDataFrame

        :param columns: columns of the STACDataFrame
        """
        stac_collection = {"crs": 4326, "properties": {}}

        for column in columns:
            if column not in ("geometry", "id"):
                stac_collection["properties"][column] = "json"

        return stac_collection

    def to_stac(self):
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
            root_output_folder = "output"
            makedirs(root_output_folder, exist_ok=True)
        else:
            for index, row in catalog_df.iterrows():
                root_output_folder = row[id_column]
                makedirs(root_output_folder, exist_ok=True)
                row_json = row.to_dict()

                # Curate the json row
                row_json = self.curate_json_row(row_json, stac_id_exists)

                with open(join(root_output_folder, f"catalog.json"), "w") as f:
                    json.dump(row_json, f)

        # Second, create the collections and their folders, if exist
        collections = dict()
        collections_df = df[df["type"] == "Collection"]
        for index, row in collections_df.iterrows():
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
        for index, row in features_df.iterrows():
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
            if (isinstance(v, float) and isnan(v)) or v == "":
                keys_to_remove.append(k)
        for key in keys_to_remove:
            del row[key]
        del row["geometry"]

        return row


def read_stac(
    stac_file: pystac.Catalog | pystac.Collection | str,
    geometry_column: str = "geometry",
) -> STACDataFrame:
    """
    Read a STAC file and return a STACDataFrame

    :param stac_file: STAC file to read
    :param geometry_column: name of the geometry column
    """
    if isinstance(stac_file, str):
        stac_file = pystac.read_file(stac_file)
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
