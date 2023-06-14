"""
Module for STAC extensions objects
"""

import pystac
from pystac.extensions.sar import SarExtension
from pystac.extensions.sar import FrequencyBand, Polarization
from pystac.extensions.eo import Band, EOExtension
from typing import Union


class STACExtensionObject:
    def __init__(self) -> None:
        super().__init__()
        self.properties = dict()

    def add_extension_to_object(
        self, obj: Union[pystac.Item, pystac.Asset]
    ) -> Union[pystac.Item, pystac.Asset]:
        """
        Add the extension to the given object

        :param obj: object to add the extension
        """
        pass


class SarExtensionObject(STACExtensionObject):
    def __init__(self) -> None:
        super().__init__()
        pass

    def add_extension_to_object(
        self, obj: Union[pystac.Item, pystac.Asset]
    ) -> Union[pystac.Item, pystac.Asset]:
        """
        Add the extension to the given object

        :param obj: object to add the extension
        """
        sar_ext = SarExtension.ext(obj, add_if_missing=True)
        if isinstance(obj, pystac.Item):
            polarizations = [Polarization.VV, Polarization.VH]
        elif isinstance(obj, pystac.Asset):
            polarizations_dict = {"VV": Polarization.VV, "VH": Polarization.VH}
            polarizations = [polarizations_dict[obj.title]]
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
        self.bands = [
            Band.create(
                name="Aerosols",
                description="Coastal aerosol, 442.7 nm (S2A), 442.3 nm (S2B)",
                common_name="coastal",
            ),
            Band.create(
                name="Blue",
                description="Blue, 492.4 nm (S2A), 492.1 nm (S2B)",
                common_name="blue",
            ),
            Band.create(
                name="Green",
                description="Green, 559.8 nm (S2A), 559.0 nm (S2B)",
                common_name="green",
            ),
            Band.create(
                name="Red",
                description="Red, 664.6 nm (S2A), 665.0 nm (S2B)",
                common_name="red",
            ),
            Band.create(
                name="Red edge 1",
                description="Vegetation red edge, 704.1 nm (S2A), 703.8 nm (S2B)",
                common_name="rededge",
            ),
            Band.create(
                name="Red edge 2",
                description="Vegetation red edge, 740.5 nm (S2A), 739.1 nm (S2B)",
                common_name="rededge",
            ),
            Band.create(
                name="Red edge 3",
                description="Vegetation red edge, 782.8 nm (S2A), 779.7 nm (S2B)",
                common_name="rededge",
            ),
            Band.create(
                name="NIR",
                description="NIR, 832.8 nm (S2A), 833.0 nm (S2B)",
                common_name="nir",
            ),
            Band.create(
                name="Red edge 4",
                description="Narrow NIR, 864.7 nm (S2A), 864.0 nm (S2B)",
                common_name="nir08",
            ),
            Band.create(
                name="Water vapour",
                description="Water vapour, 945.1 nm (S2A), 943.2 nm (S2B)",
                common_name="nir09",
            ),
            Band.create(
                name="Cirrus",
                description="SWIR – Cirrus, 1373.5 nm (S2A), 1376.9 nm (S2B)",
                common_name="cirrus",
            ),
            Band.create(
                name="SWIR1",
                description="SWIR, 1613.7 nm (S2A), 1610.4 nm (S2B)",
                common_name="swir16",
            ),
            Band.create(
                name="SWIR2",
                description="SWIR, 2202.4 nm (S2A), 2185.7 nm (S2B)",
                common_name="swir22",
            ),
        ]

    def add_extension_to_object(
        self, obj: Union[pystac.Item, pystac.Asset]
    ) -> Union[pystac.Item, pystac.Asset]:
        """
        Add the extension to the given object

        :param obj: object to add the extension
        """
        if isinstance(obj, pystac.Asset):
            return
        # Add EO extension
        eo_ext = EOExtension.ext(obj, add_if_missing=True)
        # Add the existing bands from the rasters assets list
        eo_ext.apply(bands=self.bands)
        # Add common metadata
        obj.common_metadata.constellation = "Sentinel-2"
        obj.common_metadata.platform = "Sentinel-2"
        obj.common_metadata.instruments = ["Sentinel-2"]
        obj.common_metadata.gsd = 10  # TODO Where to obtain it?

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
