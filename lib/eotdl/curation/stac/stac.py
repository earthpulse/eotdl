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
        self.extensions_funcs: dict = {
            'sentinel-1-grd': (self.add_sar_extension_to_object, self.add_sar_extension_to_object),
            'sentinel-2-l2a': (self.add_eo_s2_extension_to_item, None),
            'dem': None
        }
        self.rasters_assets: list = None

    def generate_stac_metadata(self, path: str, **kwargs) -> None:
        """
        """
        if 'catalog.json' in listdir(path):
            # Open the catalog.json as a pySTAC.Catalog object
            catalog = pystac.Catalog.from_file(f'{path}/catalog.json')
        else:
            # Create a new catalog
            id = path.split('/')[-1]
            description = kwargs.get('description', None)
            catalog = self.create_stac_catalog(id=id, description=description)
        
        # Get the list of directories in the path
        dirs = listdir(path)

        return catalog
        

    def create_stac_catalog(self, id: str, description: Optional[str] = None) -> pystac.Catalog:
        """
        """
        return pystac.Catalog(id=id, description=description)

    def create_stac_collection(self):
        """
        """
        pass

    def create_stac_item(self,
                        tiff_dir_path: str,
                        metadata_json: str,
                        extensions: Optional[list] = None
                        ) -> pystac.Item:
        """
        """
        with open(metadata_json, "r") as f:
            metadata = json.load(f)

        # Read the metadata.json associated with the raster file
        # and obtain the required info
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

        # Obtain the date acquired
        try:
            time_acquired = format_time_acquired(metadata["date-adquired"])
        except KeyError:
            return
        
        # Obtain the raster type
        type = metadata['type']
        
        # Obtain the ID from the dir name
        id = tiff_dir_path.split('/')[-1]
        
        # Instantiate pystac item
        item = pystac.Item(id=id,
                geometry=geom,
                bbox=bbox,
                datetime = time_acquired,
                properties={
                })
        
        # Get an ordered list with the raster assets
        self.rasters_assets = glob(f'{tiff_dir_path}/*.tif*')
        self.rasters_assets.sort()
        
        # Add the required extensions to the item
        item_ext_func, asset_ext_func = self.extensions_funcs[type]
        item_ext_func(item)

        # Add the assets to the item
        for raster in self.rasters_assets:
            href = raster.split('/')[-1]
            title = href.split('.')[-2]
            # Instantiate pystac asset
            asset = pystac.Asset(href=href, title=title, media_type=pystac.MediaType.GEOTIFF)
            # Add the asset to the item
            item.add_asset(title, asset)
            # Add the required extensions to the asset if required
            asset_ext_func(asset) if asset_ext_func else None

        return item

    def add_sar_extension_to_object(self, obj: pystac.Item|pystac.Asset):
        """
        Add the SAR extension to a pystac.Item object or pystac.Asset object

        :param obj: pystac.Item object or pystac.Asset object to add the extension
        """
        sar_ext = SarExtension.ext(obj, add_if_missing=True)
        if isinstance(obj, pystac.Item):
            polarizations=[Polarization.VV, Polarization.VH]
        elif isinstance(obj, pystac.Asset):
            polarizations_dict = {'VV': Polarization.VV, 'VH': Polarization.VH}
            polarizations=[polarizations_dict[obj.title]]
        sar_ext.apply(instrument_mode='EW', polarizations=polarizations, frequency_band=FrequencyBand.C, product_type='GRD')

    def add_eo_s2_extension_to_item(self, item: pystac.Item):
        """
        """
        if isinstance(item, pystac.Asset):
            return
        # Add EO extension
        eo_ext = EOExtension.ext(item, add_if_missing=True)
        # Add the existing bands from the rasters assets list
        bands = list()
        for raster in self.rasters_assets:
            raster_name = raster.split('/')[-1]
            band_name = raster_name.split('.')[0]
            band = self.sentinel_2_bands_dict[band_name]
            bands.append(band)
        eo_ext.apply(bands=bands)
        # Add common metadata
        item.common_metadata.constellation = "Sentinel-2"
        item.common_metadata.platform = "Sentinel-2"
        item.common_metadata.instruments = ["Sentinel-2"]
        item.common_metadata.gsd = 10   # Where to obtain it?
