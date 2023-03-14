from .client import get_client
import os
from datetime import timedelta

class MinioRepo():

    def __init__(self):
        self.client = get_client()
        self.bucket = os.environ["S3_BUCKET"]
        if not self.client.bucket_exists(self.bucket):
            self.client.make_bucket(self.bucket)

    def get_object(self, id):
        return f'{id}.zip'

    # def retrieve_object_file(self, id):
    #     return self.client.get_object(self.bucket,  self.get_object(id)).read()

    def retrieve_object_url(self, id):
        return self.client.get_presigned_url(
            "GET",
            self.bucket,
            self.get_object(id),
            expires=timedelta(hours=1),
        )
    
    # def persist_object(self, source, id):
    #     return self.client.fput_object(
    #         self.bucket, self.get_object(id), source
    #     )

    def persist_file(self, source, id):
        return self.client.put_object(
            self.bucket, self.get_object(id), source, length=-1, part_size=10*1024*1024,
        )

    def delete(self, id):
        object = self.get_object(id)
        return self.client.remove_object(self.bucket, object)
