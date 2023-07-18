from fastapi.exceptions import HTTPException
from fastapi import APIRouter, status, Depends
import logging
import uuid
import os
from minio.commonconfig import CopySource
import hashlib

from .auth import key_auth
from ..src.repos.mongo.client import get_db
from ..src.repos.minio.client import get_client


router = APIRouter(prefix="/migrate", tags=["migrate"])
logger = logging.getLogger(__name__)

bucket = os.environ.get("S3_BUCKET")


@router.get("", include_in_schema=False)
def migrate_db(isAdmin: bool = Depends(key_auth)):
    db = get_db()
    s3 = get_client()
    # create a backup of the changed collections
    random_id = uuid.uuid4()
    collection_name = "users-" + str(random_id)
    db[collection_name].insert_many(db["users"].find())
    # update users
    #   - rename `model_count` to `models_count`
    for user in db["users"].find():
        db["users"].update_one(
            {"_id": user["_id"]},
            {"$rename": {"model_count": "models_count"}},
        )
    collection_name = "datasets-" + str(random_id)
    db[collection_name].insert_many(db["datasets"].find())
    # update datasets
    #   - rename `author` to `autors` and convert to list
    #   - rename `link` to `source`
    #   - remove `checksum`
    #   - add `files` as a list with one value
    for dataset in db["datasets"].find():
        author = dataset["author"]
        name = dataset["name"]
        dataset_id = dataset["id"]
        size = dataset["size"]
        db["datasets"].update_one(
            {"_id": dataset["_id"]},
            {"$rename": {"author": "authors", "link": "source"}},
        )
        db["datasets"].update_one(
            {"_id": dataset["_id"]},
            {"$set": {"authors": [author]}},
        )
        db["datasets"].update_one(
            {"_id": dataset["_id"]},
            {"$unset": {"checksum": ""}},
        )
        new_object_name = f"{dataset_id}/{name}.zip"
        s3.copy_object(bucket, new_object_name, CopySource(bucket, f"{dataset_id}.zip"))
        # compute new sha1 checksum
        sha1_hash = hashlib.sha1()
        with s3.get_object(bucket, new_object_name) as stream:
            for chunk in stream.stream(1024 * 1024 * 10):
                sha1_hash.update(chunk)
            checksum = sha1_hash.hexdigest()
        db["datasets"].update_one(
            {"_id": dataset["_id"]},
            {
                "$set": {
                    "files": [
                        {
                            "name": name + ".zip",
                            "size": size,
                            "checksum": checksum,
                        }
                    ]
                }
            },
        )
    return "Done"
