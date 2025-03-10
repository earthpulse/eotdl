"""
Utils
"""

from sentinelhub import DataCollection, MosaickingOrder, MimeType
from .evalscripts import EvalScripts


class OUTPUT_FORMAT:
    TIFF = MimeType.TIFF
    JPG = MimeType.JPG
    PNG = MimeType.PNG


class SHParameters:
    """
    Sentinel Hub Parameters base class
    """

    MAX_CLOUD_COVERAGE: float = None
    FIELDS = None
    MOSAICKING_ORDER = MosaickingOrder.MOST_RECENT
    EVALSCRIPT = None
    OUTPUT_FORMAT = MimeType.TIFF

    def __init__(self):
        pass


class SHS2L2AParameters(SHParameters):
    """
    Sentinel-2-L2A parameters
    """

    DATA_COLLECTION = DataCollection.SENTINEL2_L2A
    MOSAICKING_ORDER = MosaickingOrder.LEAST_CC
    EVALSCRIPT = EvalScripts.SENTINEL_2_L2A
    FIELDS = {
        "include": ["id", "properties.datetime", "properties.eo:cloud_cover"],
        "exclude": [],
    }
    FILTER = None
    RESOLUTION = 10
    BASE_URL = "https://services.sentinel-hub.com"
    CLOUD_COVERAGE = True


class SHS2L1CParameters(SHParameters):
    """
    Sentinel-2-L1C parameters
    """

    DATA_COLLECTION = DataCollection.SENTINEL2_L1C
    MOSAICKING_ORDER = MosaickingOrder.LEAST_CC
    EVALSCRIPT = EvalScripts.SENTINEL_2_L1C
    FIELDS = {
        "include": ["id", "properties.datetime", "properties.eo:cloud_cover"],
        "exclude": [],
    }
    FILTER = None
    RESOLUTION = 10
    BASE_URL = "https://services.sentinel-hub.com"
    CLOUD_COVERAGE = True


class SHS1Parameters(SHParameters):
    """
    Sentinel-1 parameters
    """

    DATA_COLLECTION = DataCollection.SENTINEL1
    EVALSCRIPT = EvalScripts.SENTINEL_1
    MOSAICKING_ORDER = MosaickingOrder.MOST_RECENT
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
    RESOLUTION = 3
    BASE_URL = "https://services.sentinel-hub.com"
    CLOUD_COVERAGE = False


class SHDEMParameters(SHParameters):
    """
    Copernicus DEM parameters
    """

    DATA_COLLECTION = DataCollection.DEM_COPERNICUS_30
    MOSAICKING_ORDER = None
    EVALSCRIPT = EvalScripts.DEM
    FIELDS = None
    FILTER = None
    RESOLUTION = 3
    BASE_URL = "https://services.sentinel-hub.com"
    CLOUD_COVERAGE = False


class SHHarmonizedLandsatSentinel(SHParameters):
    """
    Harmonized Landsat Sentinel parameters
    """

    DATA_COLLECTION = DataCollection.HARMONIZED_LANDSAT_SENTINEL
    MOSAICKING_ORDER = MosaickingOrder.LEAST_CC
    EVALSCRIPT = EvalScripts.HLS_TRUE_COLOR
    FIELDS = None
    FILTER = None
    RESOLUTION = 10
    BASE_URL = "https://services-uswest2.sentinel-hub.com"
    CLOUD_COVERAGE = True


class SHLandsatOTL2(SHParameters):
    """
    Landsat 8-9 Collection 2 imagery processed to level 2
    """

    DATA_COLLECTION = DataCollection.LANDSAT_OT_L2
    MOSAICKING_ORDER = MosaickingOrder.LEAST_CC
    EVALSCRIPT = EvalScripts.LANDSAT_OT_L2_TRUE_COLOR
    FIELDS = None
    FILTER = None
    RESOLUTION = 10
    BASE_URL = "https://services-uswest2.sentinel-hub.com"
    CLOUD_COVERAGE = True


class DATA_COLLECTION_ID:
    SENTINEL_1_GRD = DataCollection.SENTINEL1.api_id
    SENTINEL_2_L1C = DataCollection.SENTINEL2_L1C.api_id
    SENTINEL_2_L2A = DataCollection.SENTINEL2_L2A.api_id
    DEM = DataCollection.DEM_COPERNICUS_30.api_id
    HLS = DataCollection.HARMONIZED_LANDSAT_SENTINEL.api_id
    LANDSAT_OT_L2 = DataCollection.LANDSAT_OT_L2.api_id


SUPPORTED_COLLECTION_IDS = [
    value
    for name, value in DATA_COLLECTION_ID.__dict__.items()
    if not name.startswith("__")
]

SH_PARAMETERS_DICT = {
    DATA_COLLECTION_ID.SENTINEL_1_GRD: SHS1Parameters,
    DATA_COLLECTION_ID.SENTINEL_2_L1C: SHS2L1CParameters,
    DATA_COLLECTION_ID.SENTINEL_2_L2A: SHS2L2AParameters,
    DATA_COLLECTION_ID.DEM: SHDEMParameters,
    DATA_COLLECTION_ID.HLS: SHHarmonizedLandsatSentinel,
    DATA_COLLECTION_ID.LANDSAT_OT_L2: SHLandsatOTL2,
}


def get_default_parameters(collection_id: str) -> SHParameters:
    return SH_PARAMETERS_DICT[collection_id]()


def supports_cloud_coverage(collection_id: str):
    return SH_PARAMETERS_DICT[collection_id]().CLOUD_COVERAGE
