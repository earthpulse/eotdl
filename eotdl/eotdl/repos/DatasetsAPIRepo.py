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

    def create_dataset(self, metadata, id_token):
        response = requests.post(
            self.url + "datasets",
            json=metadata,
            headers={"Authorization": "Bearer " + id_token},
        )
        return self.format_response(response)

    def retrieve_dataset(self, name):
        response = requests.get(self.url + "datasets?name=" + name)
        return self.format_response(response)

    def create_version(self, dataset_id, id_token):
        response = requests.post(
            self.url + "datasets/version/" + dataset_id,
            headers={"Authorization": "Bearer " + id_token},
        )
        return self.format_response(response)

    def create_stac_dataset(self, name, id_token):
        response = requests.post(
            self.url + "datasets/stac",
            json={"name": name},
            headers={"Authorization": "Bearer " + id_token},
        )
        return self.format_response(response)

    def ingest_stac(self, stac_json, dataset_id, id_token):
        response = requests.put(
            self.url + f"datasets/stac/{dataset_id}",
            json={"stac": stac_json},
            headers={"Authorization": "Bearer " + id_token},
        )
        return self.format_response(response)

    def download_stac(self, dataset_id, id_token):
        url = self.url + "datasets/" + dataset_id + "/download"
        headers = {"Authorization": "Bearer " + id_token}
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return None, response.json()["detail"]
        return gpd.GeoDataFrame.from_features(response.json()["features"]), None

    # def update_dataset(self, name, path, id_token, checksum):
    #     # check that dataset exists
    #     data, error = self.retrieve_dataset(name)
    #     if error:
    #         return None, error
    #     # first call to get upload id
    #     dataset_id = data["id"]
    #     url = self.url + f"datasets/chunk/{dataset_id}?checksum={checksum}"
    #     response = requests.get(url, headers={"Authorization": "Bearer " + id_token})
    #     if response.status_code != 200:
    #         return None, response.json()["detail"]
    #     data = response.json()
    #     _, upload_id, parts = data["dataset_id"], data["upload_id"], data["parts"]
    #     # assert dataset_id is None
    #     content_path = os.path.abspath(path)
    #     content_size = os.stat(content_path).st_size
    #     url = self.url + "datasets/chunk"
    #     chunk_size = 1024 * 1024 * 100  # 100 MiB
    #     total_chunks = content_size // chunk_size
    #     headers = {
    #         "Authorization": "Bearer " + id_token,
    #         "Upload-Id": upload_id,
    #         "Dataset-Id": dataset_id,
    #     }
    #     # upload chunks sequentially
    #     pbar = tqdm(
    #         self.read_in_chunks(open(content_path, "rb"), chunk_size),
    #         total=total_chunks,
    #     )
    #     index = 0
    #     for chunk in pbar:
    #         offset = index + len(chunk)
    #         part = index // chunk_size + 1
    #         index = offset
    #         if part not in parts:
    #             headers["Part-Number"] = str(part)
    #             file = {"file": chunk}
    #             r = requests.post(url, files=file, headers=headers)
    #             if r.status_code != 200:
    #                 return None, r.json()["detail"]
    #         pbar.set_description(
    #             "{:.2f}/{:.2f} MB".format(
    #                 offset / 1024 / 1024, content_size / 1024 / 1024
    #             )
    #         )
    #     pbar.close()
    #     # complete upload
    #     url = self.url + "datasets/complete"
    #     r = requests.post(
    #         url,
    #         json={"checksum": checksum},
    #         headers={
    #             "Authorization": "Bearer " + id_token,
    #             "Upload-Id": upload_id,
    #             "Dataset-Id": dataset_id,
    #         },
    #     )
    #     if r.status_code != 200:
    #         return None, r.json()["detail"]
    #     return r.json(), None
