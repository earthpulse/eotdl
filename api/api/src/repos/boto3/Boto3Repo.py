from .client import get_client
import os


class Boto3Repo:
    def __init__(self):
        self.client = get_client()
        self.bucket = os.environ["S3_BUCKET"]
        # if not self.client.bucket_exists(self.bucket):
        #     self.client.make_bucket(self.bucket)

    def multipart_upload_id(self, storage):
        return self.client.create_multipart_upload(Bucket=self.bucket, Key=storage)[
            "UploadId"
        ]

    def store_chunk(self, data, storage, part, upload_id):
        return self.client.upload_part(
            Body=data,
            Bucket=self.bucket,
            Key=storage,
            PartNumber=part,  # (offset // CHUNK_SIZE) + 1,
            UploadId=upload_id,  # request.headers.get("upload_id"),
        )

    def complete_multipart_upload(self, storage, upload_id):
        parts = self.client.list_parts(
            Bucket=self.bucket,
            Key=storage,
            UploadId=upload_id,
        )["Parts"]
        sorted_parts = sorted(parts, key=lambda part: part["PartNumber"])
        etags = [
            {"PartNumber": part["PartNumber"], "ETag": part["ETag"]}
            for part in sorted_parts
        ]
        return self.client.complete_multipart_upload(
            Bucket=self.bucket,
            Key=storage,
            MultipartUpload={"Parts": etags},
            UploadId=upload_id,
        )
