'''
Module for DEM STAC extensions object
'''

from .base import STACExtensionObject


class DEMExtensionObject(STACExtensionObject):
    DEM_DATE_ACQUIRED = {
        "start_datetime": "2011-01-01T00:00:00Z",
        "end_datetime": "2015-01-07T00:00:00Z",
    }

    def __init__(self) -> None:
        super().__init__()