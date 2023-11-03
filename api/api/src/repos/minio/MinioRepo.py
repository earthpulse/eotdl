from .client import get_client
import os
<<<<<<< HEAD:apis/eotdl/src/repos/minio/MinioRepo.py
from datetime import timedelta
=======
import hashlib
import requests
from io import BytesIO
import copy
>>>>>>> develop:api/api/src/repos/minio/MinioRepo.py


class MinioRepo:
    def __init__(self):
        self.client = get_client()
        self.bucket = os.environ["S3_BUCKET"]
        if not self.client.bucket_exists(self.bucket):
            self.client.make_bucket(self.bucket)

    def get_object(self, id):
        return f"{id}.zip"

<<<<<<< HEAD:apis/eotdl/src/repos/minio/MinioRepo.py
    def retrieve_object_file(self, id):
        return self.client.get_object(self.bucket, self.get_object(id)).read()

    def retrieve_object_url(self, id):
        return self.client.get_presigned_url(
            "GET",
            self.bucket,
            self.get_object(id),
            expires=timedelta(hours=1),
        )

    def persist_file(self, source, id):
        return self.client.put_object(
            self.bucket,
            self.get_object(id),
            source,
=======
    def persist_file(self, path_or_file, dataset_id, filename):
        object = self.get_object(dataset_id, filename)
        if isinstance(path_or_file, str):
            return self.client.fput_object(self.bucket, object, path_or_file)
        return self.client.put_object(
            self.bucket,
            object,
            path_or_file,
>>>>>>> develop:api/api/src/repos/minio/MinioRepo.py
            length=-1,
            part_size=10 * 1024 * 1024,
        )

    def persist_file_chunk(self, chunk, id, size):
        return self.client.put_object(
            self.bucket,
            self.get_object(id),
            chunk.file,
            length=size,
            part_size=chunk.size
            # self.bucket, self.get_object(id), chunk.file, length=-1, part_size=size
        )

    def delete(self, id):
        object = self.get_object(id)
        return self.client.remove_object(self.bucket, object)

    async def data_stream(self, id):
        with self.client.get_object(self.bucket, self.get_object(id)) as stream:
            for chunk in stream.stream(1024 * 1024 * 10):  # Stream in chunks of 10MB
                yield chunk

    def object_info(self, id):
        return self.client.stat_object(self.bucket, self.get_object(id))

<<<<<<< HEAD:apis/eotdl/src/repos/minio/MinioRepo.py
    def get_size(self, id):
        return self.object_info(id).size
=======
    def exists(self, dataset_id, file_name):
        try:
            self.object_info(dataset_id, file_name)
            return True
        except:
            return False

    async def calculate_checksum(self, dataset_id, file_name):
        data_stream = self.data_stream(dataset_id, file_name)
        sha1_hash = hashlib.sha1()
        async for chunk in data_stream:
            sha1_hash.update(chunk)
        return sha1_hash.hexdigest()
>>>>>>> develop:api/api/src/repos/minio/MinioRepo.py

    # def upload_id(self):
    #     return self.client.initiate_multipart_upload(
    #         self.bucket, self.get_object(id)
    #     ).upload_id
