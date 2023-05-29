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

from .utils import convert_df_geom_to_shape


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
                   server_port: int,
                   client_id: str,
                   clien_secret: str,
                   auth_aud: str):
        """
        """
        pass
    
    def to_geodb(self, 
                 server_url: str, 
                 server_port: int,
                 client_id: str, 
                 clien_secret: str, 
                 auth_aud: str,
                 collection: str,
                 database: str=None):
        """
        """
        pass

    def to_stac_file(self, root_output_folder: str='output'):
        """
        """
        makedirs(root_output_folder, exist_ok=True)
        for index, row in self.iterrows():
            # Convert the geometry from WKT back to geojson
            row['geometry'] = row['geometry'].wkt
            row['geometry'] = wkt.loads(row['geometry'])
            stac_output_folder = join(root_output_folder, row['id'])
            makedirs(stac_output_folder, exist_ok=True)
            row_json = row.to_dict()
            
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
    items = stac_file.get_all_items()

    _features = [i.to_dict() for i in items]

    # Get a new ItemCollection by removing duplicate items, if they exist
    features = []
    for f in _features:
        if f not in features:
            features.append(f)

    # Convert Dataframe to STACDataFrame
    dataframe = pd.DataFrame(features)
    dataframe[geometry_column] = dataframe.apply(convert_df_geom_to_shape, axis=1)
    stac_dataframe = STACDataFrame(dataframe, crs='EPSG:4326', geometry=gpd.GeoSeries.from_wkt(dataframe[geometry_column]))
 
    return stac_dataframe
