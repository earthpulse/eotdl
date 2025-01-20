from fastapi.exceptions import HTTPException
from fastapi import APIRouter, status, Depends, Path
import logging
from pydantic import BaseModel

from ..auth import get_current_user
from ...src.models import User
from ...src.usecases.datasets import (
    create_dataset,
    create_dataset_version,
)
from .responses import create_dataset_responses, get_dataset_version_responses

router = APIRouter()
logger = logging.getLogger(__name__)

class CreateDatasetBody(BaseModel):
    name: str

@router.post("", summary="Create a new dataset")
def create(
    body: CreateDatasetBody,
    user: User = Depends(get_current_user),
    responses=create_dataset_responses,
):
    try:
        dataset_id = create_dataset(user, body.name)
        return {"dataset_id": dataset_id}
    except Exception as e:
        logger.exception("datasets:ingest")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

@router.post(
    "/version/{dataset_id}",
    summary="Create a new version for a dataset",
    responses=get_dataset_version_responses,
)
def version_dataset(
    dataset_id: str = Path(..., description="The ID of the dataset"),
    user: User = Depends(get_current_user),
):
    """
    Create a new version for a dataset.
    """
    try:
        version = create_dataset_version(user, dataset_id)
        return {"dataset_id": dataset_id, "version": version}
    except Exception as e:
        logger.exception("datasets:version")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))