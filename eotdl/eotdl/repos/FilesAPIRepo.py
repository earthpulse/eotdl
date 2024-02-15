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
        user,
        endpoint,
        version=None,
    ):
        url = self.url + f"{endpoint}/{dataset_or_model_id}/batch"
        if version is not None:
            url += "?version=" + str(version)
        reponse = requests.post(
            url,
            files={"batch": ("batch.zip", batch)},
            data={"checksums": checksums},
            headers=self.generate_headers(user),
        )
        return self.format_response(reponse)

    def add_files_batch_to_version(
        self,
        batch,
        dataset_or_model_id,
        version,
        user,
        endpoint,
    ):
        reponse = requests.post(
            self.url + f"{endpoint}/{dataset_or_model_id}/files?version={str(version)}",
            data={
                "filenames": [f["path"] for f in batch],
                "checksums": [f["checksum"] for f in batch],
            },
            headers=self.generate_headers(user),
        )
        return self.format_response(reponse)

    def ingest_file(
        self, file, dataset_or_model_id, user, checksum, endpoint, version=None
    ):
        # TODO: ingest file URL
        url = self.url + f"{endpoint}/{dataset_or_model_id}"
        if version is not None:
            url += "?version=" + str(version)
        reponse = requests.post(
            url,
            files={"file": open(file, "rb")},
            data={"checksum": checksum},
            headers=self.generate_headers(user),
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
        user,
        path,
        file_version,
        endpoint="datasets",
        progress=False,
    ):
        url = self.url + f"{endpoint}/{dataset_or_model_id}/download/{file_name}"
        if file_version is not None:
            url += "?version=" + str(file_version)
        return self.download_file_url(url, file_name, path, user, progress=progress)

    def download_file_url(self, url, filename, path, user, progress=False):
        headers = self.generate_headers(user)
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

    def prepare_large_upload(
        self, filename, dataset_or_model_id, checksum, user, endpoint
    ):
        response = requests.post(
            self.url + f"{endpoint}/{dataset_or_model_id}/uploadId",
            json={"filname": filename, "checksum": checksum},
            headers=self.generate_headers(user),
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
        self, file_path, files_size, upload_id, user, parts, endpoint
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
                    headers=self.generate_headers(user),
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

    def complete_upload(self, user, upload_id, version, endpoint):
        r = requests.post(
            f"{self.url}{endpoint}/complete/{upload_id}?version={version}",
            headers=self.generate_headers(user),
        )
        return self.format_response(r)
