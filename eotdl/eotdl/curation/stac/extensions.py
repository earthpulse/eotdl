"""
Module for STAC extensions objects
"""

import pystac
from pystac.extensions.sar import SarExtension
from pystac.extensions.sar import FrequencyBand, Polarization
from pystac.extensions.eo import Band, EOExtension
from typing import Union
from os.path import basename, join, dirname
from os import remove

import rasterio
import pandas as pd


class STACExtensionObject:
    def __init__(self) -> None:
        super().__init__()
        self.properties = dict()

    def add_extension_to_object(
        self, obj: Union[pystac.Item, pystac.Asset],
        obj_info: pd.DataFrame=None
    ) -> Union[pystac.Item, pystac.Asset]:
        """
        Add the extension to the given object

        :param obj: object to add the extension
        """
        pass

    def extract_asset(self, 
                      raster,
                      band: str, 
                      band_index: int,
                      raster_path: str
                      ) -> pystac.Asset:
        """
        """
        raster_format = raster_path.split('.')[-1]   # Will be used later to save the bands files
        try:
            single_band = raster.read(band_index)
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
        # Instantiate pystac asset
        return pystac.Asset(href=band_name, title=band, media_type=pystac.MediaType.GEOTIFF)


class SarExtensionObject(STACExtensionObject):
    def __init__(self) -> None:
        super().__init__()
        self.polarizations = [Polarization.VV, Polarization.VH]
        self.polarizations_dict = {"VV": Polarization.VV, "VH": Polarization.VH}

    def add_extension_to_object(
        self, obj: Union[pystac.Item, pystac.Asset],
        obj_info: pd.DataFrame=None
    ) -> Union[pystac.Item, pystac.Asset]:
        """
        Add the extension to the given object

        :param obj: object to add the extension
        """
        # Add SAR extension to the item
        sar_ext = SarExtension.ext(obj, add_if_missing=True)
        if isinstance(obj, pystac.Item):
            polarizations = self.polarizations
        elif isinstance(obj, pystac.Asset):
            polarizations = [self.polarizations_dict[obj.title]]
        sar_ext.apply(
            instrument_mode="EW",
            polarizations=polarizations,
            frequency_band=FrequencyBand.C,
            product_type="GRD",
        )

        return obj


class EOS2ExtensionObject(STACExtensionObject):
    def __init__(self) -> None:
        super().__init__()
        self.bands_dict = {
            "B01": Band.create(
                name="B01",
                description="Coastal aerosol, 442.7 nm (S2A), 442.3 nm (S2B)",
                common_name="coastal",
            ),
            "B02": Band.create(
                name="B02",
                description="Blue, 492.4 nm (S2A), 492.1 nm (S2B)",
                common_name="blue",
            ),
            "B03": Band.create(
                name="B03",
                description="Green, 559.8 nm (S2A), 559.0 nm (S2B)",
                common_name="green",
            ),
            "B04": Band.create(
                name="B04",
                description="Red, 664.6 nm (S2A), 665.0 nm (S2B)",
                common_name="red",
            ),  
            "B05": Band.create(
                name="B05",
                description="Vegetation red edge, 704.1 nm (S2A), 703.8 nm (S2B)",
                common_name="rededge",
            ),
            "B06": Band.create(
                name="B06",
                description="Vegetation red edge, 740.5 nm (S2A), 739.1 nm (S2B)",
                common_name="rededge",
            ),
            "B07": Band.create(
                name="B07",
                description="Vegetation red edge, 782.8 nm (S2A), 779.7 nm (S2B)",
                common_name="rededge",
            ),
            "B08": Band.create(
                name="B08",
                description="NIR, 832.8 nm (S2A), 833.0 nm (S2B)",
                common_name="nir",
            ),
            "B08a": Band.create(
                name="B08a",
                description="Narrow NIR, 864.7 nm (S2A), 864.0 nm (S2B)",
                common_name="nir08",
            ),
            "B09": Band.create(
                name="B09",
                description="Water vapour, 945.1 nm (S2A), 943.2 nm (S2B)",
                common_name="nir09",
            ),
            "B10": Band.create(
                name="B10",
                description="SWIR – Cirrus, 1373.5 nm (S2A), 1376.9 nm (S2B)",
                common_name="cirrus",
            ),
            "B11": Band.create(
                name="B11",
                description="SWIR, 1613.7 nm (S2A), 1610.4 nm (S2B)",
                common_name="swir16",
            ),
            "B12": Band.create(
                name="B12",
                description="SWIR, 2202.4 nm (S2A), 2185.7 nm (S2B)",
                common_name="swir22",
            )
        }

    def add_extension_to_object(
        self, obj: Union[pystac.Item, pystac.Asset],
        obj_info: pd.DataFrame=None
    ) -> Union[pystac.Item, pystac.Asset]:
        """
        Add the extension to the given object

        :param obj: object to add the extension
        """
        # Add EO extension
        eo_ext = EOExtension.ext(obj, add_if_missing=True)
        # Add common metadata
        if isinstance(obj, pystac.Item):
            obj.common_metadata.constellation = "Sentinel-2"
            obj.common_metadata.platform = "Sentinel-2"
            obj.common_metadata.instruments = ["Sentinel-2"]
            obj.common_metadata.gsd = 10
            # Add bands
            bands = obj_info["bands"].values
            bands = bands[0] if bands else None
            bands_list = [self.bands_dict[band] for band in bands] if bands else None
            eo_ext.apply(bands=bands_list)

        elif isinstance(obj, pystac.Asset):
            eo_ext.apply(
                        bands=[self.bands_dict[obj.title]]
                    )

        return obj


class DEMExtensionObject(STACExtensionObject):
    DEM_DATE_ACQUIRED = {
        "start_datetime": "2011-01-01T00:00:00Z",
        "end_datetime": "2015-01-07T00:00:00Z",
    }

    def __init__(self) -> None:
        super().__init__()


type_stac_extensions_dict = {
    "sar": SarExtensionObject(),
    "eo": EOS2ExtensionObject(),
    "dem": DEMExtensionObject(),
}
