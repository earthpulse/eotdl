"""
Module for managing the Sentinel Hub configuration and data access
"""

import json
from os import getenv
from os.path import join, exists
from sentinelhub import (SHConfig, 
                         SentinelHubCatalog, 
                         BBox, 
                         bbox_to_dimensions, 
                         CRS, 
                         SentinelHubRequest, 
                         SentinelHubDownloadClient,
                         MimeType)

from ...repos.AuthRepo import AuthRepo
from .parameters import SHParameters
from .utils import check_time_interval_is_range
from datetime import datetime, timedelta


SUPPORTED_SENTINEL_MISSIONS = ('sentinel-2-l1c', 'sentinel-2-l2a', 'sentinel-1-grd')


class SHClient():
    """
    Client class to manage the Sentinel Hub Python interface.
    """

    def __init__(self
                 ) -> None:
        """
        """
        self.config = SHConfig()
        if getenv('SH_CLIENT_ID') and getenv('SH_CLIENT_SECRET'):
            # If the user has provided the credentials in a .env file, we should save them
            self.config.sh_client_id = getenv('SH_CLIENT_ID')
            self.config.sh_client_secret = getenv('SH_CLIENT_SECRET')
        else:
            # If the user has not provided the credentials, we should check if
            # the user is logged in
            auth_repo = AuthRepo()
            creds_file = auth_repo.creds_path
            if not exists(creds_file):
                raise ValueError('Your are not logged in and have not provided Sentinel Hub credentials. Please, crete a .env file with your SH_CLIENT_ID and SH_CLIENT_SECRET, or login')
            else:
                creds = json.load(open(creds_file, 'r'))
                if not 'SH_CLIENT_ID' in creds.keys() or not 'SH_CLIENT_SECRET' in creds.keys():
                    raise ValueError('If you already had a Sentinel HUB account before accepting the Terms and Conditions, your SH credentials will NOT appear here. You can retrieve them from you Sentinel HUB dashboard)')
                else:
                    self.config.sh_client_id = creds['SH_CLIENT_ID']
                    self.config.sh_client_secret = creds['SH_CLIENT_SECRET']
        self.catalog = SentinelHubCatalog(config=self.config)
        self.tmp_dir = '/tmp/sentinelhub'

    def compute_image_size(self, bounding_box, parameters):
        bbox = BBox(bbox=bounding_box, crs=CRS.WGS84)
        bbox_size = bbox_to_dimensions(bbox, resolution=parameters.RESOLUTION)

        return bbox, bbox_size   
    
    def prepare_time_interval(self, date):
        if isinstance(date, str):
            date = datetime.strptime(date, "%Y-%m-%d")
        elif isinstance(date, datetime):
            date = date.strftime("%Y-%m-%d")
        elif isinstance(date, tuple):
            if not check_time_interval_is_range(date):
                raise ValueError('The time interval must be a range of two dates, with format YYYY-MM-DD or a datetime object')
            else:
                return date
        else:
            raise ValueError('The date must be a string with format YYYY-MM-DD or a datetime object')
        date_day_before = date - timedelta(days=1)
        date_next_day = date + timedelta(days=1)
        date_day_before = date_day_before.strftime("%Y-%m-%d")
        date_next_day = date_next_day.strftime("%Y-%m-%d")

        return (date_day_before, date_next_day)

    def search_data(self,
                    bounding_box: list,
                    time_interval: list,
                    parameters: SHParameters
                    ) -> list:
        """
        """
        search_iterator = self.catalog.search(
            parameters.DATA_COLLECTION,
            bbox=BBox(bounding_box, crs=CRS.WGS84),
            time=time_interval,
            filter=parameters.FILTER,
            fields=parameters.FIELDS
        )

        return search_iterator
    
    def request_data(self,
                     time_interval,
                     bounding_box: list,
                     parameters: SHParameters
                     ) -> list:
        """
        """
        time_interval = self.prepare_time_interval(time_interval)
        bounding_box, bounding_box_size = self.compute_image_size(bounding_box, parameters)

        return SentinelHubRequest(
                    data_folder=self.tmp_dir,
                    evalscript=parameters.EVALSCRIPT,
                    input_data=[
                        SentinelHubRequest.input_data(
                            data_collection=parameters.DATA_COLLECTION,
                            time_interval=time_interval,
                            mosaicking_order=parameters.MOSAICKING_ORDER,
                        )
                    ],
                    responses=[
                                SentinelHubRequest.output_response("default", MimeType.TIFF)
                    ],
                    bbox=bounding_box,
                    size=bbox_to_dimensions(bounding_box, parameters.RESOLUTION),
                    config=self.config,
                )

    def download_data(self,
                      requests: list
                      ) -> list:
        """
        """
        download_client = SentinelHubDownloadClient(config=self.config)
        if not isinstance(requests, list):
            requests = [requests]
        download_requests = [request.download_list[0] for request in requests]
        data = download_client.download(download_requests)

        return data
