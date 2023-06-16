from .client import get_client
import os
from datetime import timedelta


class MinioRepo:
    def __init__(self):
        self.client = get_client()
        self.bucket = os.environ["S3_BUCKET"]
        if not self.client.bucket_exists(self.bucket):
            self.client.make_bucket(self.bucket)

    def get_object(self, dataset_id, file_name):
        return f"{dataset_id}/{file_name}"

    def persist_file(self, file, dataset_id):
        object = self.get_object(dataset_id, file.filename)
        return self.client.put_object(
            self.bucket,
            object,
            file.file,
            length=-1,
            part_size=10 * 1024 * 1024,
        )

    def delete(self, dataset_id, file_name):
        object = self.get_object(dataset_id, file_name)
        return self.client.remove_object(self.bucket, object)

    # def retrieve_object_file(self, id):
    #     return self.client.get_object(self.bucket, self.get_object(id)).read()

    # def retrieve_object_url(self, id):
    #     return self.client.get_presigned_url(
    #         "GET",
    #         self.bucket,
    #         self.get_object(id),
    #         expires=timedelta(hours=1),
    #     )

    # def persist_file_chunk(self, chunk, id, size):
    #     return self.client.put_object(
    #         self.bucket,
    #         self.get_object(id),
    #         chunk.file,
    #         length=size,
    #         part_size=chunk.size
    #         # self.bucket, self.get_object(id), chunk.file, length=-1, part_size=size
    #     )

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

    # def get_size(self, id):
    #     return self.object_info(id).size

    # def upload_id(self):
    #     return self.client.initiate_multipart_upload(
    #         self.bucket, self.get_object(id)
    #     ).upload_id
