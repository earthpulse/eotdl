import json
from bson import ObjectId
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

    with open("eotdl/tests/load/eotdl.tiers.copy.json", "r") as file:
        json_data = json.load(file)

    for item in json_data:
        if "_id" in item:
            item["_id"] = ObjectId(item["_id"])
    
    tiers_collection.insert_many(json_data)

    yield tiers_collection

    client.drop_database("eotdl-test")


# TODO: use this, figure out the client/bucket
@pytest.fixture
def setup_minio():
    minio_endpoint = "192.168.1.95:9000" 
    access_key = "eotdl"  
    secret_key = "12345678" 
    bucket_name = "test-bucket" 

    s3_client = boto3.client(
        "s3",
        endpoint_url=f"http://{minio_endpoint}",
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name="us-east-1",
        config=boto3.session.Config(signature_version="s3v4"),
    )

    yield s3_client

    objects = s3_client.list_objects_v2(Bucket=bucket_name)
    if "Contents" in objects:
        for obj in objects["Contents"]:
            s3_client.delete_object(Bucket=bucket_name, Key=obj["Key"])
        print(f"Deleted all objects in '{bucket_name}'.")