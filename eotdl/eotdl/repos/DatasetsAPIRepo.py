import requests
import geopandas as gpd

from ..repos import APIRepo


class DatasetsAPIRepo(APIRepo):
    def __init__(self, url=None):
        super().__init__(url)

    def retrieve_datasets(self, name, limit):
        url = self.url + "datasets"
        if name is not None:
            url += "?match=" + name
        if limit is not None:
            if name is None:
                url += "?limit=" + str(limit)
            else:
                url += "&limit=" + str(limit)
        response = requests.get(url)
        return self.format_response(response)

    def create_dataset(self, metadata, user):
        response = requests.post(
            self.url + "datasets",
            json=metadata,
            headers=self.generate_headers(user),
        )
        return self.format_response(response)

    def retrieve_dataset(self, name):
        response = requests.get(self.url + "datasets?name=" + name)
        return self.format_response(response)

    def create_version(self, dataset_id, user):
        response = requests.post(
            self.url + "datasets/version/" + dataset_id,
            headers=self.generate_headers(user),
        )
        return self.format_response(response)

    def create_stac_dataset(self, name, user):
        response = requests.post(
            self.url + "datasets/stac",
            json={"name": name},
            headers=self.generate_headers(user),
        )
        return self.format_response(response)

    def ingest_stac(self, stac_json, dataset_id, user):
        response = requests.put(
            self.url + f"datasets/stac/{dataset_id}",
            json={"stac": stac_json},
            headers=self.generate_headers(user),
        )
        return self.format_response(response)

    def download_stac(self, dataset_id, user):
        url = self.url + "datasets/" + dataset_id + "/download"
        headers = self.generate_headers(user)
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return None, response.json()["detail"]
        return gpd.GeoDataFrame.from_features(response.json()["features"]), None
