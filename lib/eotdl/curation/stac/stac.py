"""
Module for generating STAC metadata 
"""

import json
from typing import Optional
import pystac
from pystac.extensions.sar import SarExtension
from pystac.extensions.sar import FrequencyBand, Polarization
from pystac.extensions.eo import Band, EOExtension

from os import listdir

import rasterio
from rasterio.warp import transform_bounds

from datetime import datetime
from shapely.geometry import Polygon, mapping
from glob import glob

from .utils import format_time_acquired
from .extensions import type_stac_extensions_dict


class STACGenerator:

    sentinel_2_bands_dict = {
        "B01": Band.create(
            description="Central Wavelength: 442.7nm", name="Coastal Aerosol", common_name="Coastal Aerosol"
        ),
        "B02": Band.create(description="Central Wavelength: 492.4nm", name="Blue", common_name="Blue"),
        "B03": Band.create(description="Central Wavelength: 559.8nm", name="Green", common_name="Green"),
        "B04": Band.create(description="Central Wavelength: 664.6nm", name="Red", common_name="Red"),
        "B05": Band.create(description="Central Wavelength: 704.1nm", name="Vegetation Red Edge", common_name="Vegetation Red Edge"),
        "B06": Band.create(description="Central Wavelength: 740.5nm", name="Vegetation Red Edge", common_name="Vegetation Red Edge"),
        "B07": Band.create(description="Central Wavelength: 782.8nm", name="Vegetation Red Edge", common_name="Vegetation Red Edge"),
        "B08": Band.create(description="NIR: 780 - 860 nm", name="NIR", common_name="NIR"),
        "B8A": Band.create(description="Central Wavelength: 832.8nm", name="NIR", common_name="NIR"),
        "B09": Band.create(description="Water Vapour: 1360 - 1390 nm", name="Water Vapour", common_name="Water Vapour"),
        "B11": Band.create(description="SWIR: 1560 - 1660 nm", name="SWIR", common_name="SWIR"),
        "B12": Band.create(description="SWIR: 2100 - 2280 nm", name="SWIR", common_name="SWIR"),
    }
        
    def __init__(self) -> None:
        self.extensions_dict: dict = type_stac_extensions_dict
        self.rasters_assets: list = None

    def generate_stac_metadata(self, path: str, id: str, catalog_type: pystac.CatalogType = pystac.CatalogType.SELF_CONTAINED, **kwargs) -> None:
        """
        Generate STAC metadata for a given directory containing the assets to generate metadata

        :param path: path to the root directory 
        :param kwargs: optional arguments. Possible values:
            - description: description of the catalog
            - keywords: keywords of the catalog
        """
        if 'catalog.json' in listdir(path):
            # Open the catalog.json as a pySTAC.Catalog object
            catalog = pystac.Catalog.from_file(f'{path}/catalog.json')
        else:
            # Create a new catalog
            title = kwargs.get('title', None)
            description = kwargs.get('description', None)
            catalog = self.create_stac_catalog(id=id,
                                               catalog_type=catalog_type, 
                                               title=title,
                                               description=description)
            # Add the catalog to the root directory
            catalog.normalize_hrefs(path)
        
        # catalog.save(catalog_type)
        
        # Get the list of directories in the path
        dirs = listdir(path)

        return catalog   # DEBUG
        

    def create_stac_catalog(self, id: str, **kwargs) -> pystac.Catalog:
        """
        Create a STAC catalog

        :param id: id of the catalog
        :param kwargs: optional arguments. Possible values:
            - description: description of the catalog
            - keywords: keywords of the catalog
        """
        description = kwargs.get('description', None)

        return pystac.Catalog(id=id, description=description)
    
    def update_stac_catalog(self, catalog: pystac.Catalog, **kwargs) -> pystac.Catalog:
        """
        """
        # Update the catalog with the given arguments
        pass

    def create_stac_collection(self):
        """
        Create a STAC collection
        """
        pass

    def update_stacl_collection(self, collection: pystac.Collection, **kwargs) -> pystac.Collection:
        """
        Update a STAC collection
        """
        pass

    def create_stac_item(self,
                        tiff_dir_path: str,
                        metadata_json: str,
                        extensions: Optional[list|str] = None
                        ) -> pystac.Item:
        """
        Create a STAC item from a directory containing the raster files and the metadata.json file

        :param tiff_dir_path: path to the directory containing the raster files
        :param metadata_json: path to the metadata.json file
        :param extensions: list of extensions to add to the item
        :return: pystac.Item object
        """
        # Read the metadata.json associated with the raster file
        # and obtain the required info
        with open(metadata_json, "r") as f:
            metadata = json.load(f)

        # Obtain the bounding box
        bbox = metadata['bounding-box']
        left, bottom, right, top = bbox

        # Create geojson feature
        geom = mapping(Polygon([
        [left, bottom],
        [left, top],
        [right, top],
        [right, bottom]
        ]))

        # Obtain the raster type
        type = metadata['type']

        # Initialize properties
        properties = dict()

        # Obtain the date acquired
        try:
            time_acquired = format_time_acquired(metadata["date-adquired"])
        except TypeError:
            if type == 'dem':
                # If it is DEM data we don't need to add the time acquired to the item
                # But, we need to add the start and end date to the item
                time_acquired = None
                for key, item in self.extensions_dict['dem'].DEM_DATE_ACQUIRED.items():
                    properties[key] = item
            else:
                raise TypeError(f"Error: {metadata_json} does not contain a valid date acquired")
        
        # Obtain the ID from the dir name
        id = tiff_dir_path.split('/')[-1]
        
        # Instantiate pystac item
        item = pystac.Item(id=id,
                geometry=geom,
                bbox=bbox,
                datetime=time_acquired,
                properties=properties)
        
        # Get an ordered list with the raster assets
        self.rasters_assets = glob(f'{tiff_dir_path}/*.tif*')
        self.rasters_assets.sort()
        
        # Add the required extensions to the item
        if extensions:
            if isinstance(extensions, str):
                extensions = [extensions]
            for extension in extensions:
                self.extensions_dict[extension].add_extension_to_object(item)

        # Add the assets to the item
        for raster in self.rasters_assets:
            href = raster.split('/')[-1]
            title = href.split('.')[-2]
            # Instantiate pystac asset
            asset = pystac.Asset(href=href, title=title, media_type=pystac.MediaType.GEOTIFF)
            # Add the asset to the item
            item.add_asset(title, asset)
            # Add the required extensions to the asset if required
            if extensions:
                if isinstance(extensions, str):
                    extensions = [extensions]
                for extension in extensions:
                    self.extensions_dict[extension].add_extension_to_object(asset)

        return item
