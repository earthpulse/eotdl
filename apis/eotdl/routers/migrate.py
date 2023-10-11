from fastapi import APIRouter, Depends
import logging
import os
from minio.commonconfig import CopySource
from boto3.s3.transfer import TransferConfig

from .auth import key_auth
from ..src.repos.mongo.client import get_db
from ..src.repos.minio.client import get_client
from ..src.repos.boto3.client import get_client as get_boto3_client
from ..src.models import File, Files, Dataset, Version, STACDataset

from bson.objectid import ObjectId

router = APIRouter(prefix="/migrate", tags=["migrate"])
logger = logging.getLogger(__name__)

bucket = os.environ.get("S3_BUCKET")


@router.get("", include_in_schema=False)
def migrate_db(isAdmin: bool = Depends(key_auth)):
    # return "Done"
    db = get_db()
    collections = db.list_collection_names()
    # s3 = get_client()
    # boto = get_boto3_client()  # Boto3Repo()
    # create a backup of the changed collections
    collection_name = "users-bck"
    if not collection_name in collections:
        db[collection_name].insert_many(db["users"].find())
    # update users
    for user in db["users"].find():
        if "id" not in user:
            db["users"].update_one(
                {"_id": user["_id"]}, {"$set": {"id": str(user["_id"])}}
            )
    # update datasets
    #   - create files
    #   - create version
    # for dataset in db["datasets"].find():
    #     if (
    #         "size" not in dataset
    #     ):  # copy large files takes a while and api timesout, make sure this can be run multiple times
    #         continue
    #     size = dataset["size"]
    #     dataset_id = dataset["id"]
    #     if dataset["quality"] == 0:
    #         files = []
    #         for f in dataset["files"]:
    #             files.append(
    #                 File(
    #                     name=f["name"],
    #                     size=f["size"],
    #                     checksum=f["checksum"],
    #                     version=1,
    #                     versions=[1],
    #                 )
    #             )
    #             new_object_name = f"{dataset_id}/{f['name']}_1"
    #             current_name = f"{dataset_id}/{f['name']}"
    #             if size < 1024 * 1024 * 5:
    #                 # minio errors when copying files larger than 5GB
    #                 s3.copy_object(
    #                     bucket, new_object_name, CopySource(bucket, current_name)
    #                 )
    #             else:
    #                 config = TransferConfig(multipart_threshold=5 * 1024 * 1024)  # 5Mb
    #                 copy_source = {"Bucket": bucket, "Key": current_name}
    #                 boto.copy(copy_source, bucket, new_object_name, Config=config)
    #         files_id = ObjectId()
    #         data = Files(id=str(files_id), dataset=dataset_id, files=files).model_dump()
    #         data["_id"] = files_id
    #         db["files"].insert_one(data)
    #         dataset["files"] = str(files_id)
    #     version = Version(version_id=1, size=size).model_dump()
    #     dataset["versions"] = [version]
    #     del dataset["size"]
    #     updated_dataset = (
    #         Dataset(**dataset).model_dump()
    #         if dataset["quality"] == 0
    #         else STACDataset(**dataset).model_dump()
    #     )
    #     updated_dataset["_id"] = dataset["_id"]
    #     db["datasets"].delete_one({"_id": dataset["_id"]})
    #     db["datasets"].insert_one(updated_dataset)
    return "Done"
