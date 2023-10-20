'''
Module for raster STAC extensions object
'''

import pystac
import rasterio
import pandas as pd

from pystac.extensions.raster import RasterExtension, RasterBand
from typing import Union, Optional
from .base import STACExtensionObject


class RasterExtensionObject(STACExtensionObject):
    def __init__(self) -> None:
        super().__init__()

    def add_extension_to_object(
        self, obj: Union[pystac.Item, pystac.Asset],
        obj_info: Optional[pd.DataFrame] = None
    ) -> Union[pystac.Item, pystac.Asset]:
        """
        Add the extension to the given object

        :param obj: object to add the extension
        :param obj_info: object info from the STACDataFrame
        """
        if not isinstance(obj, pystac.Asset):
            return obj
        else:
            raster_ext = RasterExtension.ext(obj, add_if_missing=True)
            src = rasterio.open(obj.href)
            bands = list()
            for band in src.indexes:
                bands.append(RasterBand.create(
                    nodata=src.nodatavals[band - 1],
                    data_type=src.dtypes[band - 1],
                    spatial_resolution=src.res) if src.nodatavals else RasterBand.create(
                        data_type=src.dtypes[band - 1],
                        spatial_resolution=src.res))
            raster_ext.apply(bands=bands)
                
        return obj


