from .client import get_client
import os
import hashlib


class Boto3Repo:
    def __init__(self):
        self.client = get_client()
        self.bucket = os.environ["S3_BUCKET"]

    def multipart_upload_id(self, storage):
        return self.client.create_multipart_upload(Bucket=self.bucket, Key=storage)[
            "UploadId"
        ]

    def store_chunk(self, data, storage, part, upload_id):
        print(storage, part, upload_id)
        response = self.client.upload_part(
            Body=data,
            Bucket=self.bucket,
            Key=storage,
            PartNumber=part,  # (offset // CHUNK_SIZE) + 1,
            UploadId=upload_id,  # request.headers.get("upload_id"),
        )
        return response["ETag"].strip('"')

    def complete_multipart_upload(self, storage, upload_id):
        print(storage, upload_id)
        parts = []
        next_part_number_marker = 0
        is_truncated = True
        while is_truncated:
            response = self.client.list_parts(
                Bucket=self.bucket,
                Key=storage,
                UploadId=upload_id,
                PartNumberMarker=next_part_number_marker,
            )
            parts.extend(response["Parts"])
            is_truncated = response["IsTruncated"]
            if is_truncated:
                next_part_number_marker = response["NextPartNumberMarker"]
        sorted_parts = sorted(parts, key=lambda part: part["PartNumber"])
        parts = [
            {"PartNumber": part["PartNumber"], "ETag": part["ETag"]}
            for part in sorted_parts
        ]
        return self.client.complete_multipart_upload(
            Bucket=self.bucket,
            Key=storage,
            MultipartUpload={"Parts": parts},
            UploadId=upload_id,
        )
