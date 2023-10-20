'''
Module for EO STAC extensions object
'''

import pystac
import pandas as pd

from typing import Union
from .base import STACExtensionObject
from pystac.extensions.eo import Band, EOExtension


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
            ),
        }

    def add_extension_to_object(
        self, obj: Union[pystac.Item, pystac.Asset],
        obj_info: pd.DataFrame
    ) -> Union[pystac.Item, pystac.Asset]:
        """
        Add the extension to the given object

        :param obj: object to add the extension
        :param obj_info: object info from the STACDataFrame
        """
        # Add EO extension
        eo_ext = EOExtension.ext(obj, add_if_missing=True)
        # Add common metadata
        if isinstance(obj, pystac.Item) or (
            isinstance(obj, pystac.Asset) and obj.title not in self.bands_dict.keys()
        ):
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
            eo_ext.apply(bands=[self.bands_dict[obj.title]])

        return obj
