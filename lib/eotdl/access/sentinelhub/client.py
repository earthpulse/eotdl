"""
Module for managing the Sentinel Hub configuration and data access
"""
from sentinelhub import (SHConfig, 
                         SentinelHubCatalog, 
                         DataCollection, 
                         BBox, 
                         bbox_to_dimensions, 
                         CRS, 
                         SentinelHubRequest, 
                         MimeType)


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
                                       search_parameters: dict
                                       ) -> list:
        """
        Search and return the available Sentinel data from a given DataCollection in a selected location and time interval. 

        :param search_parameters: dict that contains the search parameters that are going to be used in the Catalog search.
                The dictionary must contain the following parameters in the following format and names:
                    - data_collection: sentinelhub.DataCollection object with the desired data collection to search. Required.
                    - bbox: list with the bounding box of the location to search in. Required.
                    - time_interval: list with the time interval stablished for the search. Required.
                    - fields: dict with the fields desired to include or exclude. Required. It must follow the format:
                        {
                        "include": list of fields to include, 
                        "exclude": list of fields to exclude
                        }
                    - filter: string with the filter to apply, if needed. Optional.
        :return results: list with the obtained results.
        """
        
        # As the filter is an optional parameter, we have to make sure that is correctly declared for the search
        if not 'filter' in search_parameters:
            filter = None
        else:
            filter = search_parameters['filter']

        search_iterator = self.catalog.search(
            search_parameters['data_collection'],
            bbox=BBox(search_parameters['bbox'], crs=CRS.WGS84),
            time=search_parameters['time_interval'],
            fields=search_parameters['fields'],
            filter=filter
        )

        results = list(search_iterator)

        return results

    def request_sentinel_data(self, 
                              data_to_download: dict, 
                              data_collection: DataCollection, 
                              evalscript: str) -> list:
        """
        Get and return a list with the download information for every location. 
        This is the prefered way to download data, as in order to efficiently 
        download data for all requests in parallel, we extract the download 
        information and we pass it to a download client.

        :param data_to_download: dict with the unique ID and bounding box of
                every location to request sentinel data from
        :param data_collection: sentinelhub.DataCollection object with the desired data collection to search.
        :param evalscript: is a piece of Javascript code which defines how the satellite data shall be 
                processed by Sentinel Hub and what values the service shall return. For further information,
                see https://docs.sentinel-hub.com/api/latest/evalscript/
        :return process_request: list with the download information for every location
        """
        self.sh_base_url = data_collection.service_url   # Use exactly the needed service url to avoid errors
        
        process_requests = list()

        for id, bbox in data_to_download.items():
            request = SentinelHubRequest(
                evalscript=evalscript,
                input_data=[
                    SentinelHubRequest.input_data(
                        data_collection=data_collection
                    )
                ],
                responses=[SentinelHubRequest.output_response("default", MimeType.TIFF)],
                bbox=BBox(bbox, crs=CRS.WGS84),
	            size=bbox_to_dimensions(bbox, resolution=5000),
                config=self,
            )
            process_requests.append(request)

        return process_requests
