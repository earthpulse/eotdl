"""
Utils
"""

from sentinelhub import DataCollection, MosaickingOrder

from .evalscripts import EvalScripts


class SHParameters:
    """
    Sentinel Hub Parameters base class
    """
    def __init__(self):
        pass


class SHS2L2AParameters(SHParameters):
    """
    Sentinel-2-L2A parameters
    """
    DATA_COLLECTION = DataCollection.SENTINEL2_L2A
    RESOLUTION = 10
    MOSAICKING_ORDER = MosaickingOrder.LEAST_CC
    EVALSCRIPT = EvalScripts.SENTINEL_2_L2A
    FIELDS = {
        "include": ["id", "properties.datetime", "properties.eo:cloud_cover"],
        "exclude": [],
    }
    FILTER = None


class SHS2L1CParameters(SHParameters):
    """
    Sentinel-2-L1C parameters
    """
    DATA_COLLECTION = DataCollection.SENTINEL2_L1C
    RESOLUTION = 10
    MOSAICKING_ORDER = MosaickingOrder.LEAST_CC
    EVALSCRIPT = EvalScripts.SENTINEL_2_L1C
    FIELDS = {
        "include": ["id", "properties.datetime", "properties.eo:cloud_cover"],
        "exclude": [],
    }


class SHS1Parameters(SHParameters):
    """
    Sentinel-1 parameters
    """
    DATA_COLLECTION = DataCollection.SENTINEL1
    RESOLUTION = 3
    EVALSCRIPT = EvalScripts.SENTINEL_1
    MOSAICKING_ORDER = None
    FIELDS = {
            "include": [
                "id",
                "properties.datetime",
                "sar:instrument_mode",
                "s1:polarization",
                "sat:orbit_state",
                "s1:resolution",
                "s1:timeliness",
            ],
            "exclude": [],
        }
    FILTER = None


class SHDEMParameters(SHParameters):
    """
    Copernicus DEM parameters
    """
    DATA_COLLECTION = DataCollection.DEM_COPERNICUS_30
    RESOLUTION = 3
    MOSAICKING_ORDER = None
    EVALSCRIPT = EvalScripts.DEM
    FILTER = None
    FIELDS = None


SUPPORTED_SENSORS = ("sentinel-1-grd", "sentinel-2-l1c", "sentinel-2-l2a", "dem")

SH_PARAMETERS_DICT = {
    "sentinel-1-grd": SHS1Parameters,
    "sentinel-2-l1c": SHS2L1CParameters,
    "sentinel-2-l2a": SHS2L2AParameters,
    "dem": SHDEMParameters,
}
