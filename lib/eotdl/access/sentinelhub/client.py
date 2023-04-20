"""
Module for managing the Sentinel Hub configuration and data access
"""
from sentinelhub import (SHConfig, 
                         SentinelHubCatalog, 
                         BBox, 
                         bbox_to_dimensions, 
                         CRS, 
                         SentinelHubRequest, 
                         MimeType)

from .utils import ParametersFeature


class EOTDLClient(SHConfig):
    """
    Child class from SHConfig, the sentinelhub-py package configuration class.
    """

    def __init__(self, sh_client_id: str, sh_client_secret: str) -> None:
        """
        :param sh_client_id: User's OAuth client ID for Sentinel Hub service.
        :param sh_client_secret: User's OAuth client secret for Sentinel Hub service.
        """
        if not sh_client_id or not sh_client_secret:
            raise("Warning! To use Sentinel Hub Catalog API, please provide the credentials (client ID and client secret).")
        
        self.sh_client_id = sh_client_id
        self.sh_client_secret = sh_client_secret
        self.catalog = SentinelHubCatalog(config=self)

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
            fields=parameters.fields,
            filter=parameters.filter
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
                    - data_to_download: Required.
                    - data_collection: Required.
                    - evalscript: Required.

        :return process_request: list with the download information for every location
        """
        self.sh_base_url = parameters.data_collection.service_url   # Use exactly the needed service url to avoid errors
        
        process_requests = list()

        for id, bbox in parameters.data_to_download.items():
            request = SentinelHubRequest(
                evalscript=parameters.evalscript,
                input_data=[
                    SentinelHubRequest.input_data(
                        data_collection=parameters.data_collection
                    )
                ],
                responses=[SentinelHubRequest.output_response("default", MimeType.TIFF)],
                bbox=BBox(bbox, crs=CRS.WGS84),
	            size=bbox_to_dimensions(bbox, resolution=5000),
                config=self,
            )
            process_requests.append(request)

        return process_requests
