"""
Module for managing the Sentinel Hub configuration and data access
"""

import json
from os import getenv
from os.path import exists
from sentinelhub import (
    SHConfig,
    SentinelHubCatalog,
    BBox,
    bbox_to_dimensions,
    CRS,
    SentinelHubRequest,
    SentinelHubDownloadClient,
    MimeType,
)

from ...repos.AuthRepo import AuthRepo
from .parameters import SHParameters
from ...tools.time_utils import prepare_time_interval
from ...tools.geo_utils import compute_image_size


class SHClient:
    """
    Client class to manage the Sentinel Hub Python interface.
    """

    def __init__(self) -> None:
        """ """
        self.config = SHConfig()
        if getenv("SH_CLIENT_ID") and getenv("SH_CLIENT_SECRET"):
            # If the user has provided the credentials in a .env file, we should save them
            self.config.sh_client_id = getenv("SH_CLIENT_ID")
            self.config.sh_client_secret = getenv("SH_CLIENT_SECRET")
        else:
            # If the user has not provided the credentials, we should check if
            # the user is logged in
            auth_repo = AuthRepo()
            creds_file = auth_repo.creds_path
            if not exists(creds_file):
                raise ValueError(
                    "Your are not logged in and have not provided Sentinel Hub credentials. Please, crete a .env file with your SH_CLIENT_ID and SH_CLIENT_SECRET, or login"
                )
            else:
                with open(creds_file, "r", encoding="utf-8") as f:
                    creds = json.load(f)
                if (
                    "SH_CLIENT_ID" not in creds.keys()
                    or "SH_CLIENT_SECRET" not in creds.keys()
                ):
                    raise ValueError(
                        "If you already had a Sentinel HUB account before accepting the Terms and Conditions, your SH credentials will NOT appear here. You can retrieve them from you Sentinel HUB dashboard)"
                    )
                else:
                    self.config.sh_client_id = creds["SH_CLIENT_ID"]
                    self.config.sh_client_secret = creds["SH_CLIENT_SECRET"]
        self.catalog = SentinelHubCatalog(config=self.config)
        self.tmp_dir = "/tmp/sentinelhub"

    def search_data(
        self, bounding_box: list, time_interval: list, parameters: SHParameters
    ) -> list:
        """
        Search data from Sentinel Hub
        """
        search_iterator = self.catalog.search(
            parameters.DATA_COLLECTION,
            bbox=BBox(bounding_box, crs=CRS.WGS84),
            time=time_interval,
            filter=parameters.FILTER,
            fields=parameters.FIELDS,
        )

        return search_iterator

    def request_data(
        self, time_interval, bounding_box: list, parameters: SHParameters
    ) -> list:
        """
        Request data from Sentinel Hub
        """
        time_interval = prepare_time_interval(time_interval)
        bounding_box, _ = compute_image_size(bounding_box, parameters)

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
            responses=[SentinelHubRequest.output_response("default", MimeType.TIFF)],
            bbox=bounding_box,
            size=bbox_to_dimensions(bounding_box, parameters.RESOLUTION),
            config=self.config,
        )

    def download_data(self, requests: list) -> list:
        """
        Download data from Sentinel Hub
        """
        download_client = SentinelHubDownloadClient(config=self.config)
        if not isinstance(requests, list):
            requests = [requests]
        download_requests = [request.download_list[0] for request in requests]
        data = download_client.download(download_requests)

        return data
