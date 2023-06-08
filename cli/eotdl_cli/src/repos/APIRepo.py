import requests
from tqdm import tqdm
from pathlib import Path
import os
from concurrent.futures import ThreadPoolExecutor
import time
import multiprocessing


class APIRepo:
    def __init__(self, url=os.getenv("EOTDL_API_URL", "https://api.eotdl.com/")):
        self.url = url

    def login(self):
        return requests.get(self.url + "auth/login")

    def token(self, code):
        return requests.get(self.url + "auth/token?code=" + code)

    def logout_url(self):
        response = requests.get(self.url + "auth/logout")
        return response.json()["logout_url"]

    def retrieve_datasets(self):
        return requests.get(self.url + "datasets").json()

    def retrieve_dataset(self, name):
        response = requests.get(self.url + "datasets?name=" + name)
        if response.status_code == 200:
            return response.json(), None
        return None, response.json()["detail"]

    def download_dataset(self, dataset_id, id_token, path):
        url = self.url + "datasets/" + dataset_id + "/download"
        headers = {"Authorization": "Bearer " + id_token}
        if path is None:
            path = str(Path.home()) + "/.etodl/datasets"
            os.makedirs(path, exist_ok=True)
        with requests.get(url, headers=headers, stream=True) as r:
            r.raise_for_status()
            total_size = int(r.headers.get("content-length", 0))
            block_size = 1024 * 1024 * 10
            progress_bar = tqdm(
                total=total_size, unit="iB", unit_scale=True, unit_divisor=1024
            )
            filename = r.headers.get("content-disposition").split("filename=")[1][1:-1]
            path = f"{path}/{filename}"
            with open(path, "wb") as f:
                for chunk in r.iter_content(block_size):
                    progress_bar.update(len(chunk))
                    if chunk:
                        f.write(chunk)
            progress_bar.close()
            return path

    def read_in_chunks(self, file_object, CHUNK_SIZE):
        while True:
            data = file_object.read(CHUNK_SIZE)
            if not data:
                break
            yield data

    def prepare_large_upload(self, name, id_token, checksum):
        url = self.url + "datasets/chunk?name=" + name + "&checksum=" + checksum
        response = requests.get(url, headers={"Authorization": "Bearer " + id_token})
        if response.status_code != 200:
            raise Exception(response.json()["detail"])
        data = response.json()
        dataset_id, upload_id, parts = (
            data["dataset_id"],
            data["upload_id"],
            data["parts"] if "parts" in data else [],
        )
        return dataset_id, upload_id, parts

    def ingest_large_dataset(
        self, path, chunk_size, upload_id, dataset_id, id_token, parts
    ):
        content_path = os.path.abspath(path)
        content_size = os.stat(content_path).st_size
        total_chunks = content_size // chunk_size
        url = self.url + "datasets/chunk"
        headers = {
            "Authorization": "Bearer " + id_token,
            "Upload-Id": upload_id,
            "Dataset-Id": dataset_id,
        }
        # upload chunks sequentially
        pbar = tqdm(
            self.read_in_chunks(open(content_path, "rb"), chunk_size),
            total=total_chunks,
        )
        index = 0
        for chunk in pbar:
            part = index // chunk_size + 1
            offset = index + len(chunk)
            index = offset
            if part not in parts:
                headers["Part-Number"] = str(part)
                file = {"file": chunk}
                r = requests.post(url, files=file, headers=headers)
                if r.status_code != 200:
                    return None, r.json()["detail"]
            pbar.set_description(
                "{:.2f}/{:.2f} MB".format(
                    offset / 1024 / 1024, content_size / 1024 / 1024
                )
            )
        pbar.close()

    def complete_upload(self, name, id_token, upload_id, dataset_id, checksum):
        url = self.url + "datasets/complete"
        r = requests.post(
            url,
            json={"name": name, "checksum": checksum},
            headers={
                "Authorization": "Bearer " + id_token,
                "Upload-Id": upload_id,
                "Dataset-Id": dataset_id,
            },
        )
        if r.status_code != 200:
            return None, r.json()["detail"]
        return r.json(), None

    def update_dataset(self, name, path, id_token, checksum):
        # check that dataset exists
        data, error = self.retrieve_dataset(name)
        if error:
            return None, error
        # first call to get upload id
        dataset_id = data["id"]
        url = self.url + f"datasets/chunk/{dataset_id}?checksum={checksum}"
        response = requests.get(url, headers={"Authorization": "Bearer " + id_token})
        if response.status_code != 200:
            return None, response.json()["detail"]
        data = response.json()
        _, upload_id, parts = data["dataset_id"], data["upload_id"], data["parts"]
        # assert dataset_id is None
        content_path = os.path.abspath(path)
        content_size = os.stat(content_path).st_size
        url = self.url + "datasets/chunk"
        chunk_size = 1024 * 1024 * 10  # 10 MiB
        total_chunks = content_size // chunk_size
        headers = {
            "Authorization": "Bearer " + id_token,
            "Upload-Id": upload_id,
            "Dataset-Id": dataset_id,
        }
        # upload chunks sequentially
        pbar = tqdm(
            self.read_in_chunks(open(content_path, "rb"), chunk_size),
            total=total_chunks,
        )
        index = 0
        for chunk in pbar:
            offset = index + len(chunk)
            part = index // chunk_size + 1
            index = offset
            if part not in parts:
                headers["Part-Number"] = str(part)
                file = {"file": chunk}
                r = requests.post(url, files=file, headers=headers)
                if r.status_code != 200:
                    return None, r.json()["detail"]
            pbar.set_description(
                "{:.2f}/{:.2f} MB".format(
                    offset / 1024 / 1024, content_size / 1024 / 1024
                )
            )
        pbar.close()
        # complete upload
        url = self.url + "datasets/complete"
        r = requests.post(
            url,
            json={"checksum": checksum},
            headers={
                "Authorization": "Bearer " + id_token,
                "Upload-Id": upload_id,
                "Dataset-Id": dataset_id,
            },
        )
        if r.status_code != 200:
            return None, r.json()["detail"]
        return r.json(), None

    # def parallel_upload(
    #     self,
    #     content_size,
    #     chunk_size,
    #     content_path,
    #     url,
    #     id_token,
    #     upload_id,
    #     dataset_id,
    #     total_chunks,
    #     threads,
    # ):
    #     # Create thread pool executor
    #     max_workers = threads if threads > 0 else multiprocessing.cpu_count()
    #     executor = ThreadPoolExecutor(max_workers=max_workers)

    #     # Divide file into chunks and create tasks for each chunk
    #     offset = 0
    #     tasks = []
    #     while offset < content_size:
    #         chunk_end = min(offset + chunk_size, content_size)
    #         tasks.append((offset, chunk_end, str(offset // chunk_size + 1)))
    #         offset = chunk_end

    #     # Define the function that will upload each chunk
    #     def upload_chunk(start, end, part):
    #         # print(f"Uploading chunk {start} - {end}", part)
    #         with open(content_path, "rb") as f:
    #             f.seek(start)
    #             chunk = f.read(end - start)
    #         # headers["Part-Number"] = part
    #         response = requests.post(
    #             url,
    #             files={"file": chunk},
    #             headers={
    #                 "Authorization": "Bearer " + id_token,
    #                 "Upload-Id": upload_id,
    #                 "Dataset-Id": dataset_id,
    #                 "Part-Number": part,
    #             },
    #         )
    #         if response.status_code != 200:
    #             print(f"Failed to upload chunk {start} - {end}")
    #         return response

    #     # Submit each task to the executor
    #     with tqdm(total=total_chunks) as pbar:
    #         futures = []
    #         for task in tasks:
    #             future = executor.submit(upload_chunk, *task)
    #             future.add_done_callback(lambda p: pbar.update())
    #             futures.append(future)

    #         # Wait for all tasks to complete
    #         for future in futures:
    #             future.result()

    # def ingest_large_dataset_parallel(self, name, description, path, id_token, threads):
    #     (
    #         content_size,
    #         chunk_size,
    #         content_path,
    #         url,
    #         upload_id,
    #         dataset_id,
    #         total_chunks,
    #     ) = self.prepare_large_upload(name, description, path, id_token)
    #     self.parallel_upload(
    #         content_size,
    #         chunk_size,
    #         content_path,
    #         url,
    #         id_token,
    #         upload_id,
    #         dataset_id,
    #         total_chunks,
    #         threads,
    #     )
    #     return self.complete_upload(name, description, id_token, upload_id, dataset_id)
