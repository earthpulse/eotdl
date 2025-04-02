from .client import get_client
import os
import hashlib
import requests
from io import BytesIO
import copy


class MinioRepo:
    def __init__(self):
        self.client = get_client()
        self.bucket = os.environ["S3_BUCKET"]
        if not self.client.bucket_exists(self.bucket):
            self.client.make_bucket(self.bucket)

    def get_object(self, dataset_id, file_name):
        return f"{dataset_id}/{file_name}"
    
    def generate_presigned_put_url(self, dataset_id, file_name):
        return self.client.presigned_put_object(
            self.bucket, self.get_object(dataset_id, file_name)
        )
    
    def get_presigned_url(self, dataset_id, file_name):
        return self.client.presigned_get_object(
            self.bucket, self.get_object(dataset_id, file_name)
        )

    def delete(self, dataset_id, file_name):
        object = self.get_object(dataset_id, file_name)
        return self.client.remove_object(self.bucket, object)
    
    def object_info(self, dataset_id, file_name):
        return self.client.stat_object(
            self.bucket, self.get_object(dataset_id, file_name)
        )

    def exists(self, dataset_id, file_name):
        try:
            self.object_info(dataset_id, file_name)
            return True
        except:
            return False

    def get_file_url(self, dataset_id, file_name):
        return self.client.presigned_get_object(
            self.bucket, self.get_object(dataset_id, file_name)
        )