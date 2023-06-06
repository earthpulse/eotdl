"""
Module for the STAC dataframe
"""

import pandas as pd
import geopandas as gpd
import pystac
import json

from xcube_geodb.core.geodb import GeoDBClient
from geomet import wkt
from os.path import join
from os import makedirs

from math import isnan
from .utils import convert_df_geom_to_shape, stac_collection, get_all_children


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
    def from_geodb(self,
                   server_url: str,
                   server_port: int | str,
                   client_id: str,
                   client_secret: str,
                   auth_aud: str,
                   collection: str,
                   database: str=None):
        """
        """
        geodb_client = GeoDBClient(server_url=server_url, 
                                   server_port=server_port, 
                                   client_id=client_id, 
                                   client_secret=client_secret, 
                                   auth_aud=auth_aud)

        return geodb_client.get_collection(collection, database=database)
    
    def to_geodb(self, 
                 server_url: str, 
                 server_port: int,
                 client_id: str, 
                 client_secret: str, 
                 auth_aud: str,
                 collection: str,
                 database: str=None):
        """
        """
        geodb_client = GeoDBClient(server_url=server_url, 
                                   server_port=server_port, 
                                   client_id=client_id, 
                                   client_secret=client_secret, 
                                   auth_aud=auth_aud)

        # Check if the collection already exists
        if geodb_client.collection_exists(collection, database=database):
            geodb_client.drop_collection(collection, database=database)

        # Rename the column id to stac_id, to avoid conflicts with the id column
        self.rename(columns={'id': 'stac_id'}, inplace=True)
        # Fill the NaN with '' to avoid errors, except in the geometry column
        copy = self.copy()
        columns_to_fill = copy.columns.drop('geometry')
        self[columns_to_fill] = self[columns_to_fill].fillna('')

        # Create the collection if it does not exist
        # and insert the data
        collections = {collection: self._create_collection_structure(self.columns)}
        geodb_client.create_collections(collections, database=database)

        geodb_client.insert_into_collection(collection, database=database, values=self)

    def _create_collection_structure(self, columns: list) -> dict:
        """
        """
        stac_collection = {
            'crs': 4326,
            'properties': {
                    }
        }

        for column in columns:
            if column not in ('geometry', 'id'):
                stac_collection['properties'][column] = 'character varying'

        return stac_collection

    def to_stac(self):
        """
        """
        df = self.copy()

        # First, create the catalog and its folder, if exists
        catalog_df = df[df['type'] == 'Catalog']
        print(catalog_df)

        if catalog_df.empty:
            root_output_folder = 'output'
            makedirs(root_output_folder, exist_ok=True)
        else:
            for index, row in catalog_df.iterrows():
                root_output_folder = row['id']
                makedirs(root_output_folder, exist_ok=True)
                row_json = row.to_dict()

                # Remove the NaN values
                # TODO meter en lista
                keys_to_remove = list()
                for k, v in row_json.items():
                    if isinstance(v, float) and isnan(v):
                        keys_to_remove.append(k)
                for key in keys_to_remove:
                    del row_json[key]
                del row_json['geometry']

                with open(join(root_output_folder, f'catalog.json'), 'w') as f:
                    json.dump(row_json, f)

        # Second, create the collections and their folders, if exist
        collections = dict()
        collections_df = df[df['type'] == 'Collection']
        for index, row in collections_df.iterrows():
            stac_output_folder = join(root_output_folder, row['id'])
            collections[row['id']] = stac_output_folder
            makedirs(stac_output_folder, exist_ok=True)
            row_json = row.to_dict()

            # Remove the NaN values
            # TODO meter en lista
            keys_to_remove = list()
            for k, v in row_json.items():
                if isinstance(v, float) and isnan(v):
                    keys_to_remove.append(k)
            for key in keys_to_remove:
                del row_json[key]
            del row_json['geometry']

            with open(join(stac_output_folder, f'collection.json'), 'w') as f:
               json.dump(row_json, f)
            
        # Then, create the items and their folders, if exist
        features_df = df[df['type'] == 'Feature']
        for index, row in features_df.iterrows():
            collection = row['collection']
            stac_output_folder = join(collections[collection], row['id'])

            # Convert the geometry from WKT back to geojson
            row['geometry'] = row['geometry'].wkt
            row['geometry'] = wkt.loads(row['geometry'])
            makedirs(stac_output_folder, exist_ok=True)
            row_json = row.to_dict()

            # Remove the NaN values
            # TODO meter en lista
            keys_to_remove = list()
            for k, v in row_json.items():
                if isinstance(v, float) and isnan(v):
                    keys_to_remove.append(k)
            for key in keys_to_remove:
                del row_json[key]
            
            with open(join(stac_output_folder, f'{row["id"]}.json'), 'w') as f:
               json.dump(row_json, f)


def read_stac(stac_file: pystac.Catalog | pystac.Collection | str, 
              geometry_column: str='geometry') -> STACDataFrame:
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
    stac_dataframe = STACDataFrame(dataframe, crs='EPSG:4326', geometry=gpd.GeoSeries.from_wkt(dataframe[geometry_column]))
 
    return stac_dataframe
