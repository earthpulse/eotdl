import requests
import geopandas as gpd

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

    def create_model(self, metadata, user):
        response = requests.post(
            self.url + "models",
            json=metadata,
            headers=self.generate_headers(user),
        )
        return self.format_response(response)

    def retrieve_model(self, name):
        response = requests.get(self.url + "models?name=" + name)
        return self.format_response(response)

    def create_version(self, model_id, user):
        response = requests.post(
            self.url + "models/version/" + model_id,
            headers=self.generate_headers(user),
        )
        return self.format_response(response)

    def update_model(
        self, model_id, authors, source, license, thumbnail, content, user
    ):
        response = requests.put(
            self.url + f"models/{model_id}",
            json={
                "authors": authors,
                "source": source,
                "license": license,
                "thumbnail": thumbnail,
                "description": content,
            },
            headers=self.generate_headers(user),
        )
        return self.format_response(response)

    def create_stac_model(self, name, user):
        response = requests.post(
            self.url + "models/stac",
            json={"name": name},
            headers=self.generate_headers(user),
        )
        return self.format_response(response)

    def ingest_stac(self, stac_json, model_id, user):
        response = requests.put(
            self.url + f"models/stac/{model_id}",
            json={"stac": stac_json},
            headers=self.generate_headers(user),
        )
        return self.format_response(response)

    def download_stac(self, model_id, user):
        url = self.url + "models/" + model_id + "/download"
        headers = self.generate_headers(user)
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return None, response.json()["detail"]
        return gpd.GeoDataFrame.from_features(response.json()["features"]), None
