"""
Module for STAC Asset Generators
"""

from os import remove, listdir
from os.path import dirname, join, basename, abspath, basename

import pandas as pd
import rasterio
import pystac

from ...tools.metadata import remove_raster_metadata


MEDIA_TYPES_DICT = {
    "tif": pystac.MediaType.GEOTIFF,
    "tiff": pystac.MediaType.GEOTIFF,
    "png": pystac.MediaType.PNG,
    "jpg": pystac.MediaType.JPEG,
    "jpeg": pystac.MediaType.JPEG,
}


class STACAssetGenerator:
    """
    Standard STAC Asset Generator
    """

    type = "None"

    def __init__(self):
        pass

    @classmethod
    def extract_assets(cls, obj_info: pd.DataFrame):
        """
        Generate a single asset from the raster file

        :param raster_path: path to the raster file
        """
        # If there is no bands, create a single band asset from the file, assuming thats a singleband raster
        raster_path = obj_info["image"].values[0]
        title = basename(raster_path).split(".")[0]
        # Get the file extension
        raster_format = raster_path.split(".")[-1]
        asset = pystac.Asset(
            href=abspath(raster_path),
            title=title,
            media_type=MEDIA_TYPES_DICT[raster_format],
            roles=["data"],
        )

        return [asset]


class BandsAssetGenerator(STACAssetGenerator):
    """
    Bands STAC Asset Generator
    """

    type = "Bands"

    def __init__(self) -> None:
        super().__init__()

    def extract_assets(self, obj_info: pd.DataFrame):
        """
        Extract the assets from the raster file from the bands column

        :param raster_path: path to the raster file
        """
        asset_list = []
        # File path
        raster_path = obj_info["image"].values[0]
        # Bands
        bands = obj_info["bands"].values
        bands = bands[0] if bands else None

        if bands:
            with rasterio.open(raster_path, "r") as raster:
                raster_name = basename(raster_path).split(".")[0]
                if isinstance(bands, str):
                    bands = [bands]
                for band in bands:
                    i = bands.index(band)
                    raster_format = raster_path.split(".")[
                        -1
                    ]  # Will be used later to save the bands files
                    try:
                        single_band = raster.read(i + 1)
                    except IndexError:
                        single_band = raster.read(1)
                    band_name = f"{raster_name}_{band}.{raster_format}"
                    output_band = join(dirname(raster_path), band_name)
                    # Copy the metadata
                    metadata = raster.meta.copy()
                    metadata.update({"count": 1})
                    # Write the band to the output folder
                    with rasterio.open(output_band, "w", **metadata) as dest:
                        dest.write(single_band, 1)
                    # Instantiate pystac asset and append it to the list
                    asset_list.append(
                        pystac.Asset(
                            href=output_band,
                            title=band,
                            media_type=MEDIA_TYPES_DICT[raster_format],
                        )
                    )

            return asset_list
