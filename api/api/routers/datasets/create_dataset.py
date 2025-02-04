from fastapi.exceptions import HTTPException
from fastapi import APIRouter, status, Depends, Body, Path
import logging
from pydantic import BaseModel
from typing import List

from ..auth import get_current_user
from ...src.models import User
from ...src.usecases.datasets import (
    create_dataset,
    # create_dataset_version,
    # create_stac_dataset,
)
from .responses import create_dataset_responses, get_dataset_version_responses

router = APIRouter()
logger = logging.getLogger(__name__)


class CreateDatasetBody(BaseModel):
    name: str
    authors: List[str]
    source: str
    license: str
    thumbnail: str
    description: str

@router.post("", summary="Create a new dataset", responses=create_dataset_responses)
def create(
    body: CreateDatasetBody = Body(..., description="Metadata of the dataset (README.md file content)"),
    user: User = Depends(get_current_user),
):
    """
    Create a new dataset. A request body must be provided, and must contain the following fields:
    - name: the name of the dataset.
    - authors: the author or authors of the dataset.
    - license: the license of the dataset.
    - source: the source of the dataset.
    - thumbnail: an image to use as the thumbnail of the dataset in the website.
    """
    try:
        dataset_id = create_dataset(
            user,
            body.name,
            body.authors,
            body.source,
            body.license,
            body.thumbnail,
            body.description,
        )
        return {"dataset_id": dataset_id}
    except Exception as e:
        logger.exception("datasets:create")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


# @router.post(
#     "/version/{dataset_id}",
#     summary="Create a new version for a dataset",
#     responses=get_dataset_version_responses,
# )
# def version_dataset(
#     dataset_id: str = Path(..., description="The ID of the dataset"),
#     user: User = Depends(get_current_user),
# ):
#     """
#     Create a new version for a dataset.
#     """
#     try:
#         version = create_dataset_version(user, dataset_id)
#         return {"dataset_id": dataset_id, "version": version}
#     except Exception as e:
#         logger.exception("datasets:version")
#         raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


# class CreateSTACDatasetBody(BaseModel):
#     name: str


# @router.post("/stac", summary="Create a new stac dataset")
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
