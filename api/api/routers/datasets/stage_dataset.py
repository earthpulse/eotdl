from fastapi.exceptions import HTTPException
from fastapi import APIRouter, status, Depends, Query, Path
import logging

from ..auth import get_current_user
from ...src.models import User
from ...src.usecases.datasets import stage_dataset_file
from .responses import download_dataset_responses as responses

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get(
    "/{dataset_id}/stage/{filename:path}",
    summary="Download a dataset",
    responses=responses,
)
async def stage_dataset(
    dataset_id: str = Path(..., description="ID of the dataset to download"),
    filename: str = Path(
        ..., description="Filename or path to the file to download from the dataset"
    ),  # podría ser un path... a/b/c/file.txt
    version: int = Query(None, description="Version of the dataset to download"),
    user: User = Depends(get_current_user),
):
    """
    Stage a dataset file from the EOTDL.
    """
    try:
        presigned_url = stage_dataset_file(dataset_id, filename, user, version)
        return {
            "presigned_url": presigned_url
        }
    except Exception as e:
        logger.exception("datasets:download")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

