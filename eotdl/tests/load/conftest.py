import json
from bson import ObjectId
from pymongo import MongoClient
import pytest


@pytest.fixture
def load_tiers(scope="function", autouse=True):
    client = MongoClient("mongodb://localhost:27017/")
    db = client["eotdl"]
    tiers_collection = db["tiers"]

    ids_to_delete = [
        ObjectId("645242248456b2cc058e43bf"),
        ObjectId("645242248456b2cc058e43c0")
    ]
    if tiers_collection.count_documents({"_id": {"$in": ids_to_delete}}) > 0:
        tiers_collection.delete_many({"_id": {"$in": ids_to_delete}})

    with open("eotdl/tests/load/eotdl.tiers.copy.json", "r") as file:
        json_data = json.load(file) 

    for item in json_data:
        if "_id" in item:
            item["_id"] = ObjectId(item["_id"])
    tiers_collection.insert_many(json_data)

    yield tiers_collection

    result = tiers_collection.delete_many({"_id": {"$in": ids_to_delete}})
    print(f"Deleted {result.deleted_count} document(s)")
