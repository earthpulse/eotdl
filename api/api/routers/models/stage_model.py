from fastapi.exceptions import HTTPException
from fastapi import APIRouter, status, Depends, Query, Path
import logging

from ..auth import get_current_user
from ...src.models import User
from ...src.usecases.models import stage_model_file
from ..models.responses import download_model_responses as responses

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get(
    "/{model_id}/stage/{filename:path}",
    summary="Download a model",
    responses=responses,
)
async def stage_model(
    model_id: str = Path(..., description="ID of the model to download"),
    filename: str = Path(
        ..., description="Filename or path to the file to download from the model"
    ),  # podría ser un path... a/b/c/file.txt
    version: int = Query(None, description="Version of the model to download"),
    user: User = Depends(get_current_user),
):
    """
    Stage a model file from the EOTDL.
    """
    try:
        presigned_url = stage_model_file(model_id, filename, user, version)
        return {
            "presigned_url": presigned_url
        }
    except Exception as e:
        logger.exception("models:download")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))