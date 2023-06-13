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
        # BUG ??? not all parts ??? local ok, cloud small files ok, cloud large files (>50GB) ko :(
        # TODO: check parts
        parts = self.client.list_parts(
            Bucket=self.bucket,
            Key=storage,
            UploadId=upload_id,
        )["Parts"]
        # maybe not needed and causing bug???
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

        # response = self.client.complete_multipart_upload(
        #     Bucket=self.bucket,
        #     Key=storage,
        #     MultipartUpload={"Parts": etags},
        #     UploadId=upload_id,
        # )
        # response_etags = [part["ETag"] for part in response["Parts"]]
        # parts_etags = [part["ETag"] for part in parts]
        # assert response_etags == parts_etags

        # Try
        # for part_number in range(1, num_parts + 1):
        #     parts.append({'PartNumber': part_number})
        # response = s3.complete_multipart_upload(Bucket='your-bucket',
        #                                         Key='your-object-key',
        #                                         UploadId=upload_id,
        #                                         MultipartUpload={'Parts': parts})
