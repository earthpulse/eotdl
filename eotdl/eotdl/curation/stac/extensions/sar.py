'''
Module for SAR STAC extensions object
'''

import pystac
import pandas as pd

from .base import STACExtensionObject

from typing import Optional, Union
from pystac.extensions.sar import SarExtension
from pystac.extensions.sar import FrequencyBand, Polarization


class SarExtensionObject(STACExtensionObject):
    def __init__(self) -> None:
        super().__init__()
        self.polarizations = [Polarization.VV, Polarization.VH]
        self.polarizations_dict = {"VV": Polarization.VV, "VH": Polarization.VH}

    def add_extension_to_object(
        self, obj: Union[pystac.Item, pystac.Asset],
        obj_info: Optional[pd.DataFrame] = None
    ) -> Union[pystac.Item, pystac.Asset]:
        """
        Add the extension to the given object

        :param obj: object to add the extension
        :param obj_info: object info from the STACDataFrame
        """
        # Add SAR extension to the item
        sar_ext = SarExtension.ext(obj, add_if_missing=True)
        if isinstance(obj, pystac.Item) or (
            isinstance(obj, pystac.Asset)
            and obj.title not in self.polarizations_dict.keys()
        ):
            polarizations = self.polarizations
        elif (
            isinstance(obj, pystac.Asset)
            and obj.title in self.polarizations_dict.keys()
        ):
            polarizations = [self.polarizations_dict[obj.title]]
        sar_ext.apply(
            instrument_mode="EW",
            polarizations=polarizations,
            frequency_band=FrequencyBand.C,
            product_type="GRD",
        )

        return obj
