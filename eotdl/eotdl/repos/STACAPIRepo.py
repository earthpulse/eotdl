import requests
import geopandas as gpd

from ..repos import APIRepo


class STACAPIRepo(APIRepo):
    def __init__(self, url=None):
        super().__init__(url)

    def status(self):
        response = requests.get(self.url + "stac")
        return self.format_response(response)


