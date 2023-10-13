from fastapi.exceptions import HTTPException
from fastapi import APIRouter, status, Depends
import logging
from pydantic import BaseModel
from typing import List

from ..auth import get_current_user
from ...src.models import User
from ...src.usecases.datasets import (
    create_dataset,
    create_dataset_version,
)  # , create_stac_dataset

router = APIRouter()
logger = logging.getLogger(__name__)


class CreateDatasetBody(BaseModel):
    name: str
    authors: List[str]
    source: str
    license: str


@router.post("")
def create(
    metadata: CreateDatasetBody,
    user: User = Depends(get_current_user),
):
    try:
        dataset_id = create_dataset(
            user, metadata.name, metadata.authors, metadata.source, metadata.license
        )
        return {"dataset_id": dataset_id}
    except Exception as e:
        logger.exception("datasets:ingest")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.post("/version/{dataset_id}")
def version_dataset(dataset_id: str, user: User = Depends(get_current_user)):
    try:
        version = create_dataset_version(user, dataset_id)
        return {"dataset_id": dataset_id, "version": version}
    except Exception as e:
        logger.exception("datasets:ingest")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


# class CreateSTACDatasetBody(BaseModel):
#     name: str

# @router.post("/stac")
# def create_stac(
#     body: CreateSTACDatasetBody,
#     user: User = Depends(get_current_user),
# ):
#     try:
#         dataset_id = create_stac_dataset(user, body.name)
#         return {"dataset_id": dataset_id}
#     except Exception as e:
#         logger.exception("datasets:ingest")
#         raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
