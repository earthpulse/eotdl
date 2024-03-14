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

    # update datasets
    collection_name = "datasets-bck"
    if not collection_name in collections:
        db[collection_name].insert_many(db["datasets"].find())
    for dataset in db["datasets"].find():
        db["datasets"].update_one({"_id": dataset["_id"]}, {"$set": {"thumbnail": ""}})
    # update models
    collection_name = "models-bck"
    if not collection_name in collections:
        db[collection_name].insert_many(db["models"].find())
    for model in db["models"].find():
        db["models"].update_one({"_id": model["_id"]}, {"$set": {"thumbnail": ""}})

    return "Done"
