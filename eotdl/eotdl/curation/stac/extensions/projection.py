'''
Module for projection STAC extensions object
'''

import pystac
import pandas as pd
import rasterio

from typing import Union
from .base import STACExtensionObject
from pystac.extensions.projection import ProjectionExtension



class ProjExtensionObject(STACExtensionObject):
    def __init__(self) -> None:
        super().__init__()

    def add_extension_to_object(
        self, obj: Union[pystac.Item, pystac.Asset],
        obj_info: pd.DataFrame
    ) -> Union[pystac.Item, pystac.Asset]:
        """
        Add the extension to the given object

        :param obj: object to add the extension
        :param obj_info: object info from the STACDataFrame
        """
        # Add raster extension to the item
        if isinstance(obj, pystac.Asset):
            return obj
        elif isinstance(obj, pystac.Item):
            proj_ext = ProjectionExtension.ext(obj, add_if_missing=True)
            ds = rasterio.open(obj_info['image'].values[0])
            # Assume all the bands have the same projection
            proj_ext.apply(
                epsg=ds.crs.to_epsg(),
                transform=ds.transform,
                shape=ds.shape,
                )

        return obj
