import json
from bson import ObjectId
from minio import Minio
from pymongo import MongoClient
import pytest
import boto3


@pytest.fixture
def setup_mongo():
    client = MongoClient("mongodb://localhost:27017/")
    db = client["eotdl-test"]

    client.drop_database("eotdl-test")

    db = client["eotdl-test"]
    tiers_collection = db["tiers"]

    with open("eotdl/tests/load/eotdl.tiers.json", "r") as file:
        json_data = json.load(file)

    for item in json_data:
        if "_id" in item:
            item["_id"] = ObjectId(item["_id"])

    tiers_collection.insert_many(json_data)

    yield tiers_collection

    client.drop_database("eotdl-test")


@pytest.fixture
def setup_minio():
    minio_client = Minio(
        "localhost:9000",
        access_key="eotdl",
        secret_key="12345678",
        secure=False, 
    )

    bucket_name = "eotdl-test"

    if not minio_client.bucket_exists(bucket_name):
        minio_client.make_bucket(bucket_name)

    objects = minio_client.list_objects(bucket_name, recursive=True)
    for obj in objects:
        minio_client.remove_object(bucket_name, obj.object_name)

    yield minio_client

    objects = minio_client.list_objects(bucket_name, recursive=True)
    for obj in objects:
        minio_client.remove_object(bucket_name, obj.object_name)
