"""
Utils
"""

from sentinelhub import DataCollection, MosaickingOrder

from ..parameters import ParametersFeature


class SHParametersFeature(ParametersFeature):
    """
    Class that allows the control of the parameters needed to search
    or download data from Sentinel Hub
    """

    def __init__(self, parameters: dict) -> None:
        """
        :param parameters: dict that contains the parameters that are going to be used to search or download Sentinel Hub data.
                The dictionary could contain the following parameters in the following format and names:
                    - data_collection: sentinelhub.DataCollection object with the desired data collection to search or download.
                    - data_to_download: dict with the unique ID and bounding box of every location to request sentinel data from.
                    - bbox: list with the bounding box of the location.
                    - time_interval: list with the time interval stablished.
                    - resolution: resolution of the image to download.
                    - data_folder: location of the directory where the fetched data will be saved.
                    - fields: dict with the fields desired to include or exclude. It must follow the format:
                        {
                        "include": list of fields to include, 
                        "exclude": list of fields to exclude
                        }
                    - filter: string with the filter to apply, if needed.
                    - evalscript: is a piece of Javascript code which defines how the satellite data shall be 
                    processed by Sentinel Hub and what values the service shall return. For further information,
                    see https://docs.sentinel-hub.com/api/latest/evalscript/
                    - mosaicking_order: sentinelhub.MosaickingOrder object with the desired mosaicking order
        """
        ParametersFeature.__init__(self, parameters)
        self.data_collection = parameters['data_collection'] if 'data_collection' in parameters else None
        self.data_to_download = parameters['data_to_download'] if 'data_to_download' in parameters else None
        self.bounding_box = parameters['bounding_box'] if 'bounding_box' in parameters else None
        self.time_interval = parameters['time_interval'] if 'time_interval' in parameters else None
        self.fields = parameters['fields'] if 'fields' in parameters else None
        self.filter = parameters['filter'] if 'filter' in parameters else None
        self.evalscript = parameters['evalscript'] if 'evalscript' in parameters else None
        self.resolution = parameters['resolution'] if 'resolution' in parameters else None
        self.data_folder = parameters['data_folder'] if 'data_folder' in parameters else None
        self.mosaicking_order = parameters['mosaicking_order'] if 'mosaicking_order' in parameters else None


options = {
        'data_collection': DataCollection.SENTINEL1,
        'fields': {"include": ["id", 
                        "properties.datetime",
                        "sar:instrument_mode", 
                        "s1:polarization",
                        "sat:orbit_state",
                        "s1:resolution",
                        "s1:timeliness"], 
            "exclude": []},
        'filter': None
    }
sentinel_1_search_parameters = SHParametersFeature(options)


options = {
        'data_collection': DataCollection.SENTINEL2_L2A,
        'fields': {"include": ["id", 
                        "properties.datetime"], 
            "exclude": []}
    }
sentinel_2_search_parameters = SHParametersFeature(options)


options = {
    'data_collection': DataCollection.SENTINEL1,
    'resolution': 3
}
sentinel_1_download_parameters = SHParametersFeature(options)


options = {
    'data_collection': DataCollection.SENTINEL2_L2A,
    'resolution': 3,
    'mosaicking_order': MosaickingOrder.LEAST_CC 
}
sentinel_2_download_parameters = SHParametersFeature(options)


options = {
    'data_collection': DataCollection.DEM_COPERNICUS_30,
    'resolution': 3
}
dem_download_parameters = SHParametersFeature(options)


class EvalScripts:
    """
    Class that defines the needed Sentinel Hub evalscripts
    """

    SENTINEL_1 = """
                //VERSION=3
                function setup() {
                    return {
                        input: [{
                            bands: ["VH", "VV"]
                        }],
                        output: {
                            id: "default",
                            bands: 2
                        }
                    };
                }

                function evaluatePixel(sample) {
                    return [sample.VH, sample.VV];
                }
                """
    
    SENTINEL_2 = """
                //VERSION=3
                function setup() {
                    return {
                        input: [{
                            bands: ["B01", 
                                    "B02", 
                                    "B03", 
                                    "B04",
                                    "B05", 
                                    "B06", 
                                    "B07", 
                                    "B08", 
                                    "B09",
                                    "B11", 
                                    "B12"]
                        }],
                        output: {
                            id: "default",
                            bands: 11
                        }
                    };
                }

                function evaluatePixel(sample) {
                    return [sample.B01, 
                            sample.B02, 
                            sample.B03, 
                            sample.B04, 
                            sample.B05, 
                            sample.B06, 
                            sample.B07, 
                            sample.B08, 
                            sample.B09,
                            sample.B11, 
                            sample.B12];
                }
                """
    
    DEM = """
        //VERSION=3

        function setup() {
            return {
                input: ["DEM"],
                output: { id: "default",
                        bands: 1,
                        sampleType: SampleType.FLOAT32
                },
            }
        }

        function evaluatePixel(sample) {
            return [sample.DEM]
        }
        """
