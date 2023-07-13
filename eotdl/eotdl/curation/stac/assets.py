'''
Module for STAC Asset Generators
'''

from os.path import dirname, join, basename

import pandas as pd
import rasterio
import pystac


class STACAssetGenerator:
    
    def __init__(self):
        pass

    def extract_assets(self, obj_info: pd.DataFrame):
        """
        Extract the assets from the raster file

        :param raster_path: path to the raster file
        """
        # If there is no bands, create a single band asset from the file, assuming thats a singleband raster
        raster_path = obj_info["image"].values[0]
        href = basename(raster_path)
        title = basename(raster_path).split('.')[0]
        asset = pystac.Asset(href=href, title=title, media_type=pystac.MediaType.GEOTIFF)

        return [asset]


class BandsAssetGenerator(STACAssetGenerator):

    def __init__(self) -> None:
        super().__init__()
    
    def extract_assets(self, obj_info: pd.DataFrame):
        """
        Extract the assets from the raster file from the bands column

        :param raster_path: path to the raster file
        """
        asset_list = []
        # File pathw
        raster_path = obj_info["image"].values[0]
        # Bands
        bands = obj_info["bands"].values
        bands = bands[0] if bands else None

        if bands:
            with rasterio.open(raster_path, 'r') as raster:
                if isinstance(bands, str):
                    bands = [bands]
                for band in bands:
                    i = bands.index(band)
                    raster_format = raster_path.split('.')[-1]   # Will be used later to save the bands files
                    try:
                        single_band = raster.read(i + 1)
                    except IndexError:
                        single_band = raster.read(1)
                    band_name = f'{band}.{raster_format}'
                    output_band = join(dirname(raster_path), band_name)
                    # Copy the metadata
                    metadata = raster.meta.copy()
                    metadata.update({"count": 1})
                    # Write the band to the output folder
                    with rasterio.open(output_band, "w", **metadata) as dest:
                        dest.write(single_band, 1)
                    # Instantiate pystac asset and append it to the list
                    asset_list.append(pystac.Asset(href=band_name, title=band, media_type=pystac.MediaType.GEOTIFF))

            return asset_list
