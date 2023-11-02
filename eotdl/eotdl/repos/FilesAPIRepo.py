import requests
import os
from tqdm import tqdm
import hashlib

from ..repos import APIRepo


class FilesAPIRepo(APIRepo):
    def __init__(self, url=None):
        super().__init__(url)

    def ingest_files_batch(
        self,
        batch,  # ziped batch of files
        checksums,
        dataset_or_model_id,
        id_token,
        endpoint,
        version=None,
    ):
        url = self.url + f"{endpoint}/{dataset_or_model_id}"
        if version is not None:
            url += "?version=" + str(version)
        reponse = requests.post(
            url,
            files={"batch": ("batch.zip", batch)},
            data={"checksums": checksums},
            headers={"Authorization": "Bearer " + id_token},
        )
        return self.format_response(reponse)

    def add_files_batch_to_version(
        self,
        batch,
        dataset_or_model_id,
        version,
        id_token,
        endpoint,
    ):
        reponse = requests.post(
            self.url + f"{endpoint}/{dataset_or_model_id}/files?version={str(version)}",
            data={
                "filenames": [f["path"] for f in batch],
                "checksums": [f["checksum"] for f in batch],
            },
            headers={"Authorization": "Bearer " + id_token},
        )
        return self.format_response(reponse)

    def ingest_file(
        self,
        file,
        dataset_or_model_id,
        version,
        parent,
        id_token,
        checksum,
        endpoint,
    ):
        reponse = requests.post(
            self.url + f"{endpoint}/{dataset_or_model_id}",
            files={"file": open(file, "rb")},
            data={"checksum": checksum, "version": version, "parent": parent}
            if checksum
            else None,
            headers={"Authorization": "Bearer " + id_token},
        )
        return self.format_response(reponse)

    def retrieve_files(self, dataset_or_model_id, endpoint, version=None):
        url = f"{self.url}{endpoint}/{dataset_or_model_id}/files"
        if version is not None:
            url += "?version=" + str(version)
        response = requests.get(url)
        return self.format_response(response)

    def download_file(
        self,
        dataset_or_model_id,
        file_name,
        id_token,
        path,
        file_version,
        endpoint="datasets",
        progress=False,
    ):
        url = self.url + f"{endpoint}/{dataset_or_model_id}/download/{file_name}"
        if file_version is not None:
            url += "?version=" + str(file_version)
        return self.download_file_url(url, file_name, path, id_token, progress=progress)

    def download_file_url(self, url, filename, path, id_token, progress=False):
        headers = {"Authorization": "Bearer " + id_token}
        path = f"{path}/{filename}"
        for i in range(1, len(path.split("/")) - 1):
            # print("/".join(path.split("/")[: i + 1]))
            os.makedirs("/".join(path.split("/")[: i + 1]), exist_ok=True)
        with requests.get(url, headers=headers, stream=True) as r:
            r.raise_for_status()
            total_size = int(r.headers.get("content-length", 0))
            block_size = 1024 * 1024 * 10
            progress = progress and total_size > 1024 * 1024 * 16
            if progress:
                progress_bar = tqdm(
                    total=total_size,
                    unit="iB",
                    unit_scale=True,
                    unit_divisor=1024,
                    position=1,
                )
            with open(path, "wb") as f:
                for chunk in r.iter_content(block_size):
                    if progress:
                        progress_bar.update(len(chunk))
                    if chunk:
                        f.write(chunk)
            if progress:
                progress_bar.close()
            return path

    # def ingest_file_url(self, file, dataset, id_token):
    #     reponse = requests.post(
    #         self.url + f"datasets/{dataset}/url",
    #         json={"url": file},
    #         headers={"Authorization": "Bearer " + id_token},
    #     )
    #     if reponse.status_code != 200:
    #         return None, reponse.json()["detail"]
    #     return reponse.json(), None

    def prepare_large_upload(
        self, filename, dataset_or_model_id, checksum, id_token, endpoint
    ):
        response = requests.post(
            self.url + f"{endpoint}/{dataset_or_model_id}/uploadId",
            json={"filname": filename, "checksum": checksum},
            headers={"Authorization": "Bearer " + id_token},
        )
        if response.status_code != 200:
            raise Exception(response.json()["detail"])
        data = response.json()
        upload_id, parts = (
            data["upload_id"],
            data["parts"] if "parts" in data else [],
        )
        return upload_id, parts

    def get_chunk_size(self, content_size):
        # adapt chunk size to content size to avoid S3 limits (10000 parts, 500MB per part, 5TB per object)
        chunk_size = 1024 * 1024 * 10  # 10 MB (up to 100 GB, 10000 parts)
        if content_size >= 1024 * 1024 * 1024 * 100:  # 100 GB
            chunk_size = 1024 * 1024 * 100  # 100 MB (up to 1 TB, 10000 parts)
        elif content_size >= 1024 * 1024 * 1024 * 1000:  # 1 TB
            chunk_size = 1024 * 1024 * 500  # 0.5 GB (up to 5 TB, 10000 parts)
        return chunk_size

    def read_in_chunks(self, file_object, CHUNK_SIZE):
        while True:
            data = file_object.read(CHUNK_SIZE)
            if not data:
                break
            yield data

    def ingest_large_file(
        self, file_path, files_size, upload_id, id_token, parts, endpoint
    ):
        print(endpoint)
        # content_path = os.path.abspath(file)
        # content_size = os.stat(content_path).st_size
        chunk_size = self.get_chunk_size(files_size)
        total_chunks = files_size // chunk_size
        # upload chunks sequentially
        pbar = tqdm(
            self.read_in_chunks(open(file_path, "rb"), chunk_size),
            total=total_chunks,
        )
        index = 0
        for chunk in pbar:
            part = index // chunk_size + 1
            offset = index + len(chunk)
            index = offset
            if part not in parts:
                checksum = hashlib.md5(chunk).hexdigest()
                response = requests.post(
                    f"{self.url}{endpoint}/chunk/{upload_id}",
                    files={"file": chunk},
                    data={"part_number": part, "checksum": checksum},
                    headers={"Authorization": "Bearer " + id_token},
                )
                if response.status_code != 200:
                    raise Exception(response.json()["detail"])
            pbar.set_description(
                "{:.2f}/{:.2f} MB".format(
                    offset / 1024 / 1024, files_size / 1024 / 1024
                )
            )
        pbar.close()
        return

    def complete_upload(self, id_token, upload_id, version, endpoint):
        r = requests.post(
            f"{self.url}{endpoint}/complete/{upload_id}?version={version}",
            headers={"Authorization": "Bearer " + id_token},
        )
        return self.format_response(r)

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
