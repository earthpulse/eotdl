"""
Module for STAC extensions objects
"""

from typing import Optional, Union
import pystac

import pandas as pd


class STACExtensionObject:
    def __init__(self) -> None:
        super().__init__()
        self.properties = dict()

    def add_extension_to_object(
        self, obj: Union[pystac.Item, pystac.Asset],
        obj_info: Optional[pd.DataFrame] = None
    ) -> Union[pystac.Item, pystac.Asset]:
        """
        Add the extension to the given object

        :param obj: object to add the extension
        :param obj_info: object info from the STACDataFrame
        """
        pass
