from .client import get_client
import os
import hashlib
import requests
from io import BytesIO


class MinioRepo:
    def __init__(self):
        self.client = get_client()
        self.bucket = os.environ["S3_BUCKET"]
        if not self.client.bucket_exists(self.bucket):
            self.client.make_bucket(self.bucket)

    def get_object(self, dataset_id, file_name):
        return f"{dataset_id}/{file_name}"

    def persist_file(self, file, dataset_id, filename):
        object = self.get_object(dataset_id, filename)
        return self.client.put_object(
            self.bucket,
            object,
            file,
            length=-1,
            part_size=10 * 1024 * 1024,
        )

    def persist_file_url(self, url, dataset_id, filename):
        object = self.get_object(dataset_id, filename)
        file_path = f"/tmp/{dataset_id}/{filename}"
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(file_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        with open(file_path, "rb") as f:
            self.client.put_object(
                self.bucket,
                object,
                f,
                length=-1,
                part_size=10 * 1024 * 1024,
            )
        os.remove(file_path)
        return

    def delete(self, dataset_id, file_name):
        object = self.get_object(dataset_id, file_name)
        return self.client.remove_object(self.bucket, object)

    async def data_stream(self, dataset_id, file_name, chunk_size=1024 * 1024 * 10):
        with self.client.get_object(
            self.bucket, self.get_object(dataset_id, file_name)
        ) as stream:
            for chunk in stream.stream(chunk_size):
                yield chunk

    def object_info(self, dataset_id, file_name):
        return self.client.stat_object(
            self.bucket, self.get_object(dataset_id, file_name)
        )

    async def calculate_checksum(self, dataset_id, file_name):
        data_stream = self.data_stream(dataset_id, file_name)
        sha1_hash = hashlib.sha1()
        async for chunk in data_stream:
            sha1_hash.update(chunk)
        return sha1_hash.hexdigest()

    def get_file_url(self, dataset_id, file_name):
        return self.client.presigned_get_object(
            self.bucket, self.get_object(dataset_id, file_name)
        )
