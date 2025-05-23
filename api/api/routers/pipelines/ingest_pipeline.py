from fastapi.exceptions import HTTPException
from fastapi import APIRouter, status, Depends, Body, Path
import logging
from pydantic import BaseModel
import traceback

from ..auth import get_current_user
from ...src.models import User
from ...src.usecases.pipelines import (
    ingest_pipeline_file,
    complete_pipeline_ingestion,
)

router = APIRouter()
logger = logging.getLogger(__name__)


class IngestPipelineBody(BaseModel):
    file_name: str

@router.post(
    "/{pipeline_id}",
    summary="Ingest file to a pipeline",
)
async def ingest_files(
    pipeline_id: str = Path(..., description="ID of the pipeline"),
    body: IngestPipelineBody = Body(..., description="Metadata of the pipeline (README.md file content)"),
    user: User = Depends(get_current_user),
):
    """
    Ingest file to existing pipeline. 
    """
    try:
        presigned_url = await ingest_pipeline_file(
            body.file_name, pipeline_id, user
        )
        return {
            "presigned_url": presigned_url,
        }
    except Exception as e:
        logger.exception("pipelines:ingest")
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

class CompleteIngestionBody(BaseModel):
    version: int
    size: int

@router.post(
    "/complete/{pipeline_id}",
    summary="Complete the ingestion of a pipeline",
)
def complete_ingestion(
    pipeline_id: str = Path(..., description="ID of the pipeline"),
    body: CompleteIngestionBody = Body(..., description="Version and size of the pipeline"),
    user: User = Depends(get_current_user),
):
    try:
        complete_pipeline_ingestion(pipeline_id, user, body.version, body.size)
        return {
            "message": "Ingestion completed"
        }
    except Exception as e:
        logger.exception("pipelines:ingest")
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))