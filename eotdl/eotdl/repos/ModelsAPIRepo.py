import requests
import os

from ..repos import APIRepo


class ModelsAPIRepo(APIRepo):
    def __init__(self, url=None):
        super().__init__(url)

    def retrieve_models(self, name, limit):
        url = self.url + "models"
        if name is not None:
            url += "?match=" + name
        if limit is not None:
            if name is None:
                url += "?limit=" + str(limit)
            else:
                url += "&limit=" + str(limit)
        response = requests.get(url)
        return self.format_response(response)
