"""
Module for STAC extensions objects
"""

import pystac
from pystac.extensions.sar import SarExtension
from pystac.extensions.sar import FrequencyBand, Polarization
from pystac.extensions.eo import Band, EOExtension
from pystac.extensions.label import (LabelClasses, LabelExtension, SummariesLabelExtension)
from pystac.extensions.raster import RasterExtension, RasterBand
from pystac.extensions.projection import ProjectionExtension
from typing import Union
from os.path import basename, join, dirname
from os import remove

import rasterio
import pandas as pd


SUPPORTED_EXTENSIONS = ('eo', 'sar', 'proj', 'raster')


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
        if isinstance(obj, pystac.Item) or (isinstance(obj, pystac.Asset) and obj.title not in self.polarizations_dict.keys()):
            polarizations = self.polarizations
        elif isinstance(obj, pystac.Asset) and obj.title in self.polarizations_dict.keys():
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
        if isinstance(obj, pystac.Item) or (isinstance(obj, pystac.Asset) and obj.title not in self.bands_dict.keys()):
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


class LabelExtensionObject(STACExtensionObject):
    def __init__(self) -> None:
        super().__init__()

    @classmethod
    def add_extension_to_item(
        self, 
        obj: pystac.Item,
        href: str,
        label_names: list[str],
        label_classes: list[str],
        label_properties: list,
        label_description: str,
        label_methods: list,
        label_tasks: list[str],
        label_type: str
    ) -> Union[pystac.Item, pystac.Asset]:
        """
        Add the extension to the given object

        :param obj: object to add the extension
        """
        label_item = pystac.Item(id=obj.id,
                                     geometry=obj.geometry,
                                     bbox=obj.bbox,
                                     properties=dict(),
                                     datetime=obj.datetime
                                    )
        
        # Add the label extension to the item
        LabelExtension.add_to(label_item)

        # Access the label extension
        label_ext = LabelExtension.ext(label_item)

        # Add the label classes
        for name, classes in zip(label_names, label_classes):
            label_classes = LabelClasses.create(
                name=name,
                classes=classes,
                )
            label_ext.label_classes = [label_classes]

        # Add the label properties
        label_ext.label_properties = label_properties
        # Add the label description
        label_ext.label_description = label_description
        # Add the label methods
        label_ext.label_methods = label_methods
        # Add the label type
        label_ext.label_type = label_type
        # Add the label tasks
        label_ext.label_tasks = label_tasks
        # Add the source
        label_ext.add_source(obj)
        # Set self href
        label_item.set_self_href(join(dirname(href), f'{obj.id}.json'))

        return label_item
    
    @classmethod
    def add_extension_to_collection(
            self,
            obj: pystac.Collection,
            label_names: list[str],
            label_classes: list[list|tuple],
            label_type: str
    ) -> None:
        """
        """
        LabelExtension.add_to(obj)
        
        # Add the label extension to the collection
        label_ext = SummariesLabelExtension(obj)

        # Add the label classes
        for name, classes in zip(label_names, label_classes):
            label_classes = LabelClasses.create(
                name=name,
                classes=classes,
                )
            label_ext.label_classes = [label_classes]

        # Add the label type
        label_ext.label_type = label_type


class RasterExtensionObject(STACExtensionObject):
    def __init__(self) -> None:
        super().__init__()

    def add_extension_to_object(
        self, obj: Union[pystac.Item, pystac.Asset],
        obj_info: pd.DataFrame=None
    ) -> Union[pystac.Item, pystac.Asset]:
        """
        Add the extension to the given object

        :param obj: object to add the extension
        """
        if not isinstance(obj, pystac.Asset):
            return obj
        elif isinstance(obj, pystac.Asset):
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


class ProjExtensionObject(STACExtensionObject):
    def __init__(self) -> None:
        super().__init__()

    def add_extension_to_object(
        self, obj: Union[pystac.Item, pystac.Asset],
        obj_info: pd.DataFrame=None
    ) -> Union[pystac.Item, pystac.Asset]:
        """
        Add the extension to the given object

        :param obj: object to add the extension
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


type_stac_extensions_dict = {
    "sar": SarExtensionObject(),
    "eo": EOS2ExtensionObject(),
    "dem": DEMExtensionObject(),
    "raster": RasterExtensionObject(),
    "proj": ProjExtensionObject()
}
