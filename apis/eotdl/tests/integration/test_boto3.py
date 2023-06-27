import pytest
import os

from ...src.repos.boto3.client import get_client
from ...src.repos.boto3 import Boto3Repo

bucket = os.environ.get("S3_BUCKET")


@pytest.fixture
def s3():
    s3 = get_client()
    test_path = os.path.join(os.path.dirname(__file__), "../test.zip")
    s3.upload_file(test_path, bucket, "dataset/file")
    yield s3
    response = s3.list_objects(Bucket=bucket)
    if "Contents" in response:
        objects = [{"Key": k} for k in [obj["Key"] for obj in response["Contents"]]]
        s3.delete_objects(Bucket=bucket, Delete={"Objects": objects})


def test_multipart_upload(s3):
    repo = Boto3Repo()
    upload_id = repo.multipart_upload_id("dataset/file")
    assert isinstance(upload_id, str)
    test_path = os.path.join(os.path.dirname(__file__), "../test.zip")
    chunk_size = 5 * 1024 * 1024  # 5 MB chunk size (adjust as needed)
    part_number = 1  # Part number starts from 1
    parts = []
    with open(test_path, "rb") as file:
        while True:
            data = file.read(chunk_size)
            if not data:
                break
            checksum = repo.store_chunk(data, "dataset/file", part_number, upload_id)
            assert isinstance(checksum, str)
    repo.complete_multipart_upload("dataset/file", upload_id)
    assert s3.head_object(Bucket=bucket, Key="dataset/file")[
        "ContentLength"
    ] == os.path.getsize(test_path)
