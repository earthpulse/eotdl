from fastapi import APIRouter, Depends
import logging
import os
from minio.commonconfig import CopySource
import hashlib
from boto3.s3.transfer import TransferConfig

from .auth import key_auth
from ..src.repos.mongo.client import get_db
from ..src.repos.minio.client import get_client
from ..src.repos.boto3.client import get_client as get_boto3_client
from ..src.repos.boto3 import Boto3Repo


router = APIRouter(prefix="/migrate", tags=["migrate"])
logger = logging.getLogger(__name__)

bucket = os.environ.get("S3_BUCKET")


@router.get("", include_in_schema=False)
def migrate_db(isAdmin: bool = Depends(key_auth)):
    db = get_db()
    collections = db.list_collection_names()
    s3 = get_client()
    boto = get_boto3_client()  # Boto3Repo()
    # create a backup of the changed collections
    collection_name = "users-bck"
    if not collection_name in collections:
        db[collection_name].insert_many(db["users"].find())
    # update users
    #   - rename `model_count` to `models_count`
    for user in db["users"].find():
        if "model_count" in user:
            db["users"].update_one(
                {"_id": user["_id"]},
                {"$rename": {"model_count": "models_count"}},
            )
    collection_name = "datasets-bck"
    if not collection_name in collections:
        db[collection_name].insert_many(db["datasets"].find())
    # update datasets
    #   - rename `author` to `autors` and convert to list
    #   - rename `link` to `source`
    #   - remove `checksum`
    #   - add `files` as a list with one value
    for dataset in db["datasets"].find():
        print("updating dataset", dataset["name"])
        name = dataset["name"]
        dataset_id = dataset["id"]
        size = dataset["size"]
        if "author" in dataset:
            author = dataset["author"]
            db["datasets"].update_one(
                {"_id": dataset["_id"]},
                {"$rename": {"author": "authors", "link": "source"}},
            )
            db["datasets"].update_one(
                {"_id": dataset["_id"]},
                {"$set": {"authors": [author]}},
            )
        if "checksum" in dataset:
            db["datasets"].update_one(
                {"_id": dataset["_id"]},
                {"$unset": {"checksum": ""}},
            )
        if not "authors" in dataset or dataset["authors"] == [""]:
            db["datasets"].update_one(
                {"_id": dataset["_id"]},
                {"$set": {"authors": ["-"]}},
            )
        if not "license" in dataset or dataset["license"] == "":
            db["datasets"].update_one(
                {"_id": dataset["_id"]},
                {"$set": {"license": "-"}},
            )
        if not "files" in dataset:
            new_object_name = f"{dataset_id}/{name}.zip"
            print(f"{dataset_id}.zip")
            if size < 1024 * 1024 * 5:
                # minio errors when copying files larger than 5GB
                s3.copy_object(
                    bucket, new_object_name, CopySource(bucket, f"{dataset_id}.zip")
                )
            else:
                # quizás tengo que poner aquí un if en el caso que ya lo haya copiado pero no haya calculado checksum
                config = TransferConfig(multipart_threshold=5 * 1024 * 1024)  # 5Mb
                copy_source = {"Bucket": bucket, "Key": f"{dataset_id}.zip"}
                boto.copy(copy_source, bucket, new_object_name, Config=config)
                # need to do a multipart upload
                # upload_id = boto.multipart_upload_id(new_object_name)
                # part = 1
                # with s3.get_object(bucket, f"{dataset_id}.zip") as stream:
                #     for chunk in stream.stream(1024 * 1024 * 1024):  # 1GB
                #         boto.store_chunk(
                #             chunk,
                #             new_object_name,
                #             part,
                #             upload_id,
                #         )
                #         part += 1
                # boto.complete_multipart_upload(new_object_name, upload_id)
            # compute new sha1 checksum
            sha1_hash = hashlib.sha1()
            with s3.get_object(bucket, new_object_name) as stream:
                for chunk in stream.stream(1024 * 1024 * 10):
                    sha1_hash.update(chunk)
                checksum = sha1_hash.hexdigest()
            # add files list
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
