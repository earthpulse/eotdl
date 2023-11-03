import pytest
import os
from bson import ObjectId

from api.src.repos.mongo.client import get_db
from api.src.repos.minio.client import get_client
from api.src.repos.boto3.client import get_client as get_boto_client

datasets = [
    {
        "uid": "123",
        "name": "test1",
        "files": [{"name": "test.zip", "size": 123, "checksum": "123"}],
    },
    {
        "uid": "123",
        "name": "test2",
        "files": [{"name": "test.zip", "size": 123, "checksum": "123"}],
    },
    {
        "uid": "123",
        "name": "test3",
        "likes": 1,
        "files": [{"name": "test.zip", "size": 123, "checksum": "123"}],
    },
    {
        "uid": "123",
        "name": "test4",
        "likes": 2,
        "files": [{"name": "test.zip", "size": 123, "checksum": "123"}],
    },
    {
        "uid": "123",
        "name": "test5",
        "likes": 3,
        "tags": ["tag1", "tag2"],
        "files": [{"name": "test.zip", "size": 123, "checksum": "123"}],
    },
    {
        "uid": "456",
        "name": "test6",
        "files": [{"name": "test.zip", "size": 123, "checksum": "123"}],
    },
]

users = [
    {
        "id": str(ObjectId()),
        "uid": "123",
        "name": "test",
        "email": "test",
        "picture": "test",
        "tier": "dev",
        "dataset_count": 3,
    },
    {
        "id": str(ObjectId()),
        "uid": "456",
        "name": "test2",
        "email": "test2",
        "picture": "test2",
        "dataset_count": 10,
    },
]


tiers = [
    {
        "name": "dev",
        "limits": {
            "datasets": {"upload": 1000, "download": 1000, "count": 10, "files": 10}
        },
    },
    {
        "name": "free",
        "limits": {"datasets": {"upload": 1, "download": 1, "count": 10, "files": 10}},
    },
]

tags = [
    {"name": "tag1"},
    {"name": "tag2"},
    {"name": "tag3"},
]


@pytest.fixture
def db():
    db = get_db()
    for d in datasets:
        d["_id"] = ObjectId()
        d["id"] = str(d["_id"])
    db["datasets"].insert_many(datasets)
    users[0]["liked_datasets"] = [datasets[2]["id"], datasets[3]["id"]]
    db["users"].insert_many(users)
    db["tiers"].insert_many(tiers)
    db["tags"].insert_many(tags)
    yield db
    db.drop_collection("users")
    db.drop_collection("tiers")
    db.drop_collection("datasets")
    db.drop_collection("tags")


BUCKET = os.environ.get("S3_BUCKET")


@pytest.fixture
def s3():
    s3 = get_client()
    if not s3.bucket_exists(BUCKET):
        s3.make_bucket(BUCKET)
    test_path = os.path.join(os.path.dirname(__file__), "../test.zip")
    for d in datasets:
        s3.fput_object(BUCKET, f'{d["_id"]}/test.zip', test_path)
    yield s3
    for obj in s3.list_objects(BUCKET, recursive=True):
        s3.remove_object(BUCKET, obj.object_name)
    s3.remove_bucket(BUCKET)


@pytest.fixture
def boto3():
    s3 = get_boto_client()
    yield s3


@pytest.fixture
def bucket():
    return BUCKET
