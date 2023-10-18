"""
Module for managing the Sentinel Hub configuration and data access
"""

import json
from os.path import join, exists
from typing import Optional
from sentinelhub import (SHConfig, 
                         SentinelHubCatalog, 
                         BBox, 
                         bbox_to_dimensions, 
                         CRS, 
                         SentinelHubRequest, 
                         SentinelHubDownloadClient,
                         MimeType)

from ...repos.AuthRepo import AuthRepo
from .parameters import (SHParametersFeature, 
                         sentinel_1_search_parameters, 
                         sentinel_2_search_parameters)


SENTINEL_PARAMETERS = {'sentinel-1': sentinel_1_search_parameters,
                       'sentinel-2': sentinel_2_search_parameters}


class SHClient():
    """
    Client class to manage the Sentinel Hub Python interface.
    """

    def __init__(self,
                 sh_client_id: Optional[str] = None, 
                 sh_client_secret: Optional[str] = None
                 ) -> None:
        """
        :param sh_client_id: User's OAuth client ID for Sentinel Hub service.
        :param sh_client_secret: User's OAuth client secret for Sentinel Hub service.
        """
        self.config = SHConfig()
        if sh_client_id and sh_client_secret:
            # If the user has provided the credentials, we should save them
            self.config.sh_client_id = sh_client_id
            self.config.sh_client_secret = sh_client_secret
        else:
            # If the user has not provided the credentials, we should check if
            # the user is logged in
            auth_repo = AuthRepo()
            creds_file = auth_repo.creds_path
            if not exists(creds_file):
                raise ValueError('Your are not logged in and have not provided Sentinel Hub credentials.')
            else:
                creds = json.load(open(creds_file, 'r'))
                if not 'SH_CLIENT_ID' in creds.keys() or not 'SH_CLIENT_SECRET' in creds.keys():
                    raise ValueError('If you already had a Sentinel HUB account before accepting the Terms and Conditions, your SH credentials will NOT appear here. You can retrieve them from you Sentinel HUB dashboard)')
                else:
                    self.config.sh_client_id = creds['SH_CLIENT_ID']
                    self.config.sh_client_secret = creds['SH_CLIENT_SECRET']
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
            _data_folder = join(root_folder, id)

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
                    evalscript=parameters.evalscript,
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

    def get_available_data_by_location(self,
                                       search_data: dict,
                                       sentinel_mission: str
                                       ) -> list:
        """
        Search and return a dict with the available Sentinel data for a dict with given locations and a time intervals.

        :param search_data: dictionary with the data required to search the available imagery in a given location
                and time interval. It must have the following format:
                    {<location_id>: {'bounding_box': list(), 'time_interval': list()}, ... }
        :param sentinel_mission: id of the required Sentinel mission. The value must be <sentinel-1> or <sentinel-2>
        
        :return: available_data: available data for downloading for a given location and time interval
        :return: not_available_data: list with the locations that does not have any available data for the
                given location and time interval
        """
        if sentinel_mission not in ('sentinel-1', 'sentinel-2'):
            raise ValueError('The specified Sentinel mission is not valid. The values must be between <sentinel-1> and <sentinel-2>')
        
        parameters = SENTINEL_PARAMETERS[sentinel_mission]

        available_data, not_available_data = dict(), list()
        for location_id, location_info in search_data.items():
            parameters.bounding_box = location_info['bounding_box']
            parameters.time_interval = location_info['time_interval']
            results = self.search_available_sentinel_data(parameters)
            if results:
                # The returning results are composed by a list with format 
                # 'id': <image ID>, properties : {'datetime': <image date>}
                # As we can't make a bulk request with the ID but with the date time,
                # and we need all the available images in a time lapse and not
                # a mosaic, we are going to generate a dict with format
                # 'location_id': <location ID>,
                # {'bounding_box': <image bbox>, 'time_interval': <image date>}
                # This dictionary is digerible by the SHClient
                time_intervals = list()
                for result in results:
                    datetime = result['properties']['datetime'][0:10]
                    time_interval = (datetime, datetime)
                    time_intervals.append(time_interval) if time_interval not in time_intervals else time_intervals
                available_data[location_id] = {'bounding_box': location_info['bounding_box'], 'time_interval': time_intervals}
            else:
                # We should have a trace with the locations without
                # available data
                not_available_data.append(location_id)

        return available_data, not_available_data
