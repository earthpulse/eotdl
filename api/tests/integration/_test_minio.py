import pytest
import os

from api.src.repos.minio.client import get_client
from api.src.repos.minio import MinioRepo

bucket = os.environ.get("S3_BUCKET")

# TODO: generate and cleanup test files


@pytest.fixture
def s3():
    s3 = get_client()
    test_path = os.path.join(os.path.dirname(__file__), "../test.zip")
    s3.fput_object(bucket, "dataset/file", test_path)
    yield s3
    for obj in s3.list_objects(bucket):
        s3.remove_object(bucket, obj.object_name)


def test_get_object():
    repo = MinioRepo()
    assert repo.get_object("dataset", "file") == "dataset/file"


def test_persist_file(s3):
    repo = MinioRepo()
    test_path = os.path.join(os.path.dirname(__file__), "../test.zip")
    file = open(test_path, "rb")
    repo.persist_file(file, "dataset", "file")
    assert s3.stat_object(bucket, "dataset/file").size == os.path.getsize(test_path)


def test_delete(s3):
    repo = MinioRepo()
    repo.delete("dataset", "file")
    print([o.object_name for o in list(s3.list_objects(bucket))])
    assert list(s3.list_objects(bucket)) == []
