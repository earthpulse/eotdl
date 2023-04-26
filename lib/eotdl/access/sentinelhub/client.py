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
                         MimeType)

from .utils import ParametersFeature


class EOTDLClient():
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
                                       parameters: ParametersFeature
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

    def request_sentinel_data(self, 
                              parameters: ParametersFeature
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
                                                time_interval: list(time_interval)
                                                )
                    - data_collection: Required.
                    - evalscript: Required.
                    - resolution: Required.
                    - data_folder: Required.

        :return process_request: list with the download information for every location
        """
        self.sh_base_url = parameters.data_collection.service_url   # Use exactly the needed service url to avoid errors
        
        process_requests = list()

        for id, info in parameters.data_to_download.items():
            # We should distinct between the possible input formats
            if isinstance(info, tuple):
                bbox = BBox(info, crs=CRS.WGS84)
                time = None
            elif isinstance(info, dict):
                bbox = BBox(info['bounding_box'], crs=CRS.WGS84)
                time = info['time_interval']
            # Create a different data folder for each request
            data_folder = join(parameters.data_folder, f'{parameters.data_collection.api_id}_{id}')

            request = SentinelHubRequest(
                data_folder=data_folder,
                evalscript=parameters.evalscript,
                input_data=[
                    SentinelHubRequest.input_data(
                        data_collection=parameters.data_collection,
                        time_interval=time
                    )
                ],
                responses=[SentinelHubRequest.output_response("default", MimeType.TIFF)],
                bbox=bbox,
	            size=bbox_to_dimensions(bbox, parameters.resolution),
                config=self,
            )
            process_requests.append(request)

        return process_requests

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
