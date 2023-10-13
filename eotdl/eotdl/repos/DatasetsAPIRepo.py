import requests
import os

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

    # def create_stac_dataset(self, name, id_token):
    #     response = requests.post(
    #         self.url + "datasets/stac",
    #         json={"name": name},
    #         headers={"Authorization": "Bearer " + id_token},
    #     )
    #     if response.status_code == 200:
    #         return response.json(), None
    #     return None, response.json()["detail"]

    # def download_file(self, dataset, dataset_id, file, id_token, path):
    #     url = self.url + "datasets/" + dataset_id + "/download/" + file
    #     return self.download_file_url(url, path, id_token, progress=True)

    # def download_file_url(self, url, path, id_token, progress=False):
    #     headers = {"Authorization": "Bearer " + id_token}
    #     filename = url.split("/")[-1]
    #     os.makedirs(path, exist_ok=True)
    #     path = f"{path}/{filename}"
    #     with requests.get(url, headers=headers, stream=True) as r:
    #         r.raise_for_status()
    #         total_size = int(r.headers.get("content-length", 0))
    #         block_size = 1024 * 1024 * 10
    #         if progress:
    #             progress_bar = tqdm(
    #                 total=total_size, unit="iB", unit_scale=True, unit_divisor=1024
    #             )
    #         with open(path, "wb") as f:
    #             for chunk in r.iter_content(block_size):
    #                 if progress:
    #                     progress_bar.update(len(chunk))
    #                 if chunk:
    #                     f.write(chunk)
    #         if progress:
    #             progress_bar.close()
    #         return path

    # def ingest_file_url(self, file, dataset, id_token):
    #     reponse = requests.post(
    #         self.url + f"datasets/{dataset}/url",
    #         json={"url": file},
    #         headers={"Authorization": "Bearer " + id_token},
    #     )
    #     if reponse.status_code != 200:
    #         return None, reponse.json()["detail"]
    #     return reponse.json(), None

    # def read_in_chunks(self, file_object, CHUNK_SIZE):
    #     while True:
    #         data = file_object.read(CHUNK_SIZE)
    #         if not data:
    #             break
    #         yield data

    # def prepare_large_upload(self, file, dataset_id, checksum, id_token):
    #     filename = Path(file).name
    #     response = requests.post(
    #         self.url + f"datasets/{dataset_id}/uploadId",
    #         json={"name": filename, "checksum": checksum},
    #         headers={"Authorization": "Bearer " + id_token},
    #     )
    #     if response.status_code != 200:
    #         raise Exception(response.json()["detail"])
    #     data = response.json()
    #     upload_id, parts = (
    #         data["upload_id"],
    #         data["parts"] if "parts" in data else [],
    #     )
    #     return upload_id, parts

    # def get_chunk_size(self, content_size):
    #     # adapt chunk size to content size to avoid S3 limits (10000 parts, 500MB per part, 5TB per object)
    #     chunk_size = 1024 * 1024 * 10  # 10 MB (up to 100 GB, 10000 parts)
    #     if content_size >= 1024 * 1024 * 1024 * 100:  # 100 GB
    #         chunk_size = 1024 * 1024 * 100  # 100 MB (up to 1 TB, 10000 parts)
    #     elif content_size >= 1024 * 1024 * 1024 * 1000:  # 1 TB
    #         chunk_size = 1024 * 1024 * 500  # 0.5 GB (up to 5 TB, 10000 parts)
    #     return chunk_size

    # def ingest_large_dataset(self, file, upload_id, id_token, parts):
    #     content_path = os.path.abspath(file)
    #     content_size = os.stat(content_path).st_size
    #     chunk_size = self.get_chunk_size(content_size)
    #     total_chunks = content_size // chunk_size
    #     # upload chunks sequentially
    #     pbar = tqdm(
    #         self.read_in_chunks(open(content_path, "rb"), chunk_size),
    #         total=total_chunks,
    #     )
    #     index = 0
    #     for chunk in pbar:
    #         part = index // chunk_size + 1
    #         offset = index + len(chunk)
    #         index = offset
    #         if part not in parts:
    #             checksum = hashlib.md5(chunk).hexdigest()
    #             response = requests.post(
    #                 self.url + "datasets/chunk/" + upload_id,
    #                 files={"file": chunk},
    #                 data={"part_number": part, "checksum": checksum},
    #                 headers={"Authorization": "Bearer " + id_token},
    #             )
    #             if response.status_code != 200:
    #                 raise Exception(response.json()["detail"])
    #         pbar.set_description(
    #             "{:.2f}/{:.2f} MB".format(
    #                 offset / 1024 / 1024, content_size / 1024 / 1024
    #             )
    #         )
    #     pbar.close()
    #     return

    # def complete_upload(self, id_token, upload_id):
    #     r = requests.post(
    #         self.url + "datasets/complete/" + upload_id,
    #         headers={"Authorization": "Bearer " + id_token},
    #     )
    #     if r.status_code != 200:
    #         return None, r.json()["detail"]
    #     return r.json(), None

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

    # def delete_file(self, dataset_id, file_name, id_token):
    #     response = requests.delete(
    #         self.url + "datasets/" + dataset_id + "/file/" + file_name,
    #         headers={"Authorization": "Bearer " + id_token},
    #     )
    #     if response.status_code != 200:
    #         return None, response.json()["detail"]
    #     return response.json(), None

    # def ingest_stac(self, stac_json, dataset_id, id_token):
    #     reponse = requests.put(
    #         self.url + f"datasets/stac/{dataset_id}",
    #         json={"stac": stac_json},
    #         headers={"Authorization": "Bearer " + id_token},
    #     )
    #     if reponse.status_code != 200:
    #         return None, reponse.json()["detail"]
    #     return reponse.json(), None

    # def download_stac(self, dataset_id, id_token):
    #     url = self.url + "datasets/" + dataset_id + "/download"
    #     headers = {"Authorization": "Bearer " + id_token}
    #     response = requests.get(url, headers=headers)
    #     if response.status_code != 200:
    #         return None, response.json()["detail"]
    #     return gpd.GeoDataFrame.from_features(response.json()["features"]), None
