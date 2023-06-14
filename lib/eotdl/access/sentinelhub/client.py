"""
Module for managing the Sentinel Hub configuration and data access
"""
from os.path import join
from sentinelhub import (SHConfig, 
                         SentinelHubCatalog, 
                         BBox, 
                         bbox_to_dimensions, 
                         CRS, 
                         SentinelHubRequest, 
                         SentinelHubDownloadClient,
                         MimeType,
                         DataCollection)

from .utils import SHParametersFeature, EvalScripts

# Relate the DataCollection.api_id with the corresponding evalscript
# We will use it in the SHClient.request_data function
data_collection_evalscripts = {'sentinel-1-grd': EvalScripts.SENTINEL_1,
                               'sentinel-2-l2a': EvalScripts.SENTINEL_2,
                               'dem': EvalScripts.DEM}


class SHClient():
    """
    Client class to manage the Sentinel Hub Python interface.
    """

    def __init__(self, 
                 sh_client_id: str, 
                 sh_client_secret: str
                 ) -> None:
        """
        :param sh_client_id: User's OAuth client ID for Sentinel Hub service.
        :param sh_client_secret: User's OAuth client secret for Sentinel Hub service.
        """
        self.config = SHConfig()
        self.config.sh_client_id = sh_client_id
        self.config.sh_client_secret = sh_client_secret
        self.catalog = SentinelHubCatalog(config=self.config)

    def search_available_sentinel_data(self,
                                       parameters: SHParametersFeature
                                       ) -> list:
        """
        Search and return the available Sentinel data from a given DataCollection in a selected location and time interval. 

        :param parameters: ParametersFeature object with the needed parameters for the search. The neeeded parameters are:
                    - data_collection: Required.
                    - bbox: Required.
                    - time_interval: Required.
                    - fields: Required.
                    - filter: Optional.
        :return results: list with the obtained results.
        """
        search_iterator = self.catalog.search(
            parameters.data_collection,
            bbox=BBox(parameters.bounding_box, crs=CRS.WGS84),
            time=parameters.time_interval,
            filter=parameters.filter,
            fields=parameters.fields
        )

        results = list(search_iterator)

        return results

    def request_bulk_data(self, 
                    parameters: SHParametersFeature
                    ) -> list:
        """
        Get and return a list with the download information for every location. 
        This is the prefered way to download data, as in order to efficiently 
        download data for all requests in parallel, we extract the download 
        information and we pass it to a download client.

        :param parameters: ParametersFeature object with the needed parameters for the search. The neeeded parameters are:
                    - data_to_download: Required. Dictionary with the information about the data that the user wants to
                        download. It could have two formats:
                            - location_id : list(bounding_box)
                            - location_id : dict(bounding_box: list(bounding_box),
                                                time_interval: list(list(time_interval), list(time_interval) ...)
                                                )
                    - data_collection: Required.
                    - resolution: Required.
                    - data_folder: Required.

        :return process_request: list with the download information for every location
        """
        # Use exactly the needed service url to avoid errors
        self.config.sh_base_url = parameters.data_collection.service_url   
        
        process_requests = list()

        root_folder = parameters.data_folder

        for id, info in parameters.data_to_download.items():
            # We should distinct between the possible input formats
            if isinstance(info, tuple):
                bbox = BBox(info, crs=CRS.WGS84)
                time_interval = [None]
            elif isinstance(info, dict):   # Bulk download
                bbox = BBox(info['bounding_box'], crs=CRS.WGS84)
                time_interval = info['time_interval']
            parameters.bounding_box = bbox

            # Create a different data folder for each request
            _data_folder = join(root_folder, f'{parameters.data_collection.api_id}_{id}')

            for time in time_interval:
                # Add the date to the data folder name, if it exists
                data_folder = f'{_data_folder}_{time[1]}' if time else _data_folder
                # Add required parameters to the ParametersFeature, in order to
                # pass it to the request data function
                parameters.data_folder = data_folder
                parameters.time_interval = time
                # Do the request and append it to the requests list 
                request = self.request_data(parameters)
                process_requests.append(request)

        return process_requests
    
    def request_data(self, 
                    parameters: SHParametersFeature
                    ) -> list:
        """
        Request the specified Sentinel Hub data and return the SentinelHubRequest object

        :param parameters: ParametersFeature object with the needed parameters for the search. The neeeded parameters are:
                    - time_interval: Required.
                    - data_collection: Required.
                    - resolution: Required.
                    - data_folder: Required.
                    - bounding_box: Required.
                    - mosaicking_order: Optional.

        """
        return SentinelHubRequest(
                    data_folder=parameters.data_folder,
                    evalscript=data_collection_evalscripts[parameters.data_collection.api_id],
                    input_data=[
                        SentinelHubRequest.input_data(
                            data_collection=parameters.data_collection,
                            time_interval=parameters.time_interval,
                            mosaicking_order=parameters.mosaicking_order
                        )
                    ],
                    responses=[
                                SentinelHubRequest.output_response("default", MimeType.TIFF)
                    ],
                    bbox=parameters.bounding_box,
                    size=bbox_to_dimensions(parameters.bounding_box, parameters.resolution),
                    config=self.config,
                )

    def download_data(self,
                      requests: list
                      ) -> list:
        """
        Download data from Sentinel Hub Services using a list of requests. 
        This is the prefered way to download data, in order to efficiently 
        download data for all requests in parallel.
        
        :param requests: list with SentinelHubRequest objects representing each 
                        request to the Sentinel Hub Services.
        :return: list with the downloaded data
        """
        download_client = SentinelHubDownloadClient(config=self.config)
        download_requests = [request.download_list[0] for request in requests]
        # Download data with multiple threads
        data = download_client.download(download_requests)

        return data
