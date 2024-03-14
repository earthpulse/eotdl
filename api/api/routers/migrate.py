from fastapi import APIRouter, Depends
import logging
import os
from minio.commonconfig import CopySource
from boto3.s3.transfer import TransferConfig

from .auth import admin_key_auth
from ..src.repos.mongo.client import get_db
from ..src.repos.minio.client import get_client
from ..src.repos.boto3.client import get_client as get_boto3_client
from ..src.models import File, Files, Dataset, Version, STACDataset

from bson.objectid import ObjectId

router = APIRouter(prefix="/migrate", tags=["migrate"])
logger = logging.getLogger(__name__)

bucket = os.environ.get("S3_BUCKET")


@router.get("", include_in_schema=False)
def migrate_db(isAdmin: bool = Depends(admin_key_auth)):
    # return "Done"

    db = get_db()
    collections = db.list_collection_names()
    # s3 = get_client()
    # boto = get_boto3_client()  # Boto3Repo()

    # update files
    collection_name = "files-bck"
    if not collection_name in collections:
        db[collection_name].insert_many(db["files"].find())
    for files in db["files"].find():
        # db["files"].update_one({"_id": files["_id"]}, {"$set": {"thumbnail": ""}})

        # remove all dicts in the files's files array with name `metadata.yml`
        db["files"].update_one(
            {"_id": files["_id"]},
            {"$pull": {"files": {"name": "metadata.yml"}}},
        )

    return "Done"
