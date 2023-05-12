"""
Module for STAC extensions objects
"""

import pystac
from pystac.extensions.sar import SarExtension
from pystac.extensions.sar import FrequencyBand, Polarization
from pystac.extensions.eo import Band, EOExtension


class STACExtensionObject:

    def __init__(self) -> None:
        super().__init__()
        self.properties = dict()
    
    def add_extension_to_object(self, obj: pystac.Item|pystac.Asset) -> pystac.Item|pystac.Asset:
        """
        Add the extension to the given object
        
        :param obj: object to add the extension
        """
        pass


class SarExtensionObject(STACExtensionObject):

    def __init__(self) -> None:
        super().__init__()
        pass

    def add_extension_to_object(self, obj: pystac.Item|pystac.Asset) -> pystac.Item|pystac.Asset:
        """
        Add the extension to the given object
        
        :param obj: object to add the extension
        """
        sar_ext = SarExtension.ext(obj, add_if_missing=True)
        if isinstance(obj, pystac.Item):
            polarizations=[Polarization.VV, Polarization.VH]
        elif isinstance(obj, pystac.Asset):
            polarizations_dict = {'VV': Polarization.VV, 'VH': Polarization.VH}
            polarizations=[polarizations_dict[obj.title]]
        sar_ext.apply(instrument_mode='EW', polarizations=polarizations, frequency_band=FrequencyBand.C, product_type='GRD')

        return obj
    

class EOS2ExtensionObject(STACExtensionObject):

    def __init__(self) -> None:
        super().__init__()
        pass

    def add_extension_to_object(self, obj: pystac.Item|pystac.Asset) -> pystac.Item|pystac.Asset:
        """
        Add the extension to the given object
        
        :param obj: object to add the extension
        """
        if isinstance(obj, pystac.Asset):
            return
        # Add EO extension
        eo_ext = EOExtension.ext(obj, add_if_missing=True)
        # Add the existing bands from the rasters assets list
        bands = list()
        for raster in self.rasters_assets:
            raster_name = raster.split('/')[-1]
            band_name = raster_name.split('.')[0]
            band = self.sentinel_2_bands_dict[band_name]
            bands.append(band)
        eo_ext.apply(bands=bands)
        # Add common metadata
        obj.common_metadata.constellation = "Sentinel-2"
        obj.common_metadata.platform = "Sentinel-2"
        obj.common_metadata.instruments = ["Sentinel-2"]
        obj.common_metadata.gsd = 10   # Where to obtain it?

        return obj


class DEMExtensionObject(STACExtensionObject):

    DEM_DATE_ACQUIRED = {"start_datetime": "2011-01-01T00:00:00Z",
                        "end_datetime": "2015-01-07T00:00:00Z"}

    def __init__(self) -> None:
        super().__init__()


type_stac_extensions_dict = {
    'sar': SarExtensionObject(),
    'eo-s2': EOS2ExtensionObject(),
    'dem': DEMExtensionObject()
}