from fastapi.exceptions import HTTPException
from fastapi import APIRouter, status, Depends, Query, Path
import logging

from ..auth import get_current_user
from ...src.models import User
from ...src.usecases.pipelines import stage_pipeline_file, read_file
import traceback

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get(
    "/{pipeline_id}/stage/{filename:path}",
    summary="Stage a pipeline file",
)
async def stage_pipeline(
    pipeline_id: str = Path(..., description="ID of the pipeline to stage"),
    filename: str = Path(
        ..., description="Filename or path to the file to download from the pipeline"
    ),  # podría ser un path... a/b/c/file.txt
    version: int = Query(None, description="Version of the pipeline to stage"),
    user: User = Depends(get_current_user),
):
    """
    Stage a pipeline file from the EOTDL.
    """
    try:
        presigned_url = stage_pipeline_file(pipeline_id, filename, user, version)
        return {
            "presigned_url": presigned_url
        }
    except Exception as e:
        logger.exception("pipelines:download")
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    

@router.get(
    "/{pipeline_id}/raw/{filename:path}",
    summary="Get raw content of a pipeline file",
)
async def raw_pipeline(
    pipeline_id: str = Path(..., description="ID of the pipeline to stage"),
    filename: str = Path(
        ..., description="Filename or path to the file to download from the pipeline"
    ),  # podría ser un path... a/b/c/file.txt
    version: int = Query(None, description="Version of the pipeline to stage"),
    # user: User = Depends(get_current_user),
):
    """
    Get raw content of a pipeline file from the EOTDL.
    """
    try:
        # I guess content should be json serializable...
        return read_file(pipeline_id, filename, version)
    except Exception as e:
        logger.exception("pipelines:download")
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))