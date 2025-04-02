from fastapi.exceptions import HTTPException
from fastapi import APIRouter, status, Depends, Body, Form, UploadFile, Path, Query
import logging
from typing import List
from pydantic import BaseModel

from ..auth import get_current_user
from ...src.models import User
from ...src.usecases.models import (
    ingest_model_file,
    complete_model_ingestion,
)
from .responses import ingest_files_responses

router = APIRouter()
logger = logging.getLogger(__name__)


class IngestModelBody(BaseModel):
    file_name: str

@router.post(
    "/{model_id}",
    summary="Ingest file to a model",
    responses=ingest_files_responses,
)
async def ingest_files(
    model_id: str = Path(..., description="ID of the model"),
    # version: int = Query(None, description="Version of the dataset"),
    # file: UploadFile = File(
    #     ..., description="file to ingest"
    # ),
    # checksum: str = Form(
    #     ...,
    #     description="checksum of the file to ingest, calculated with SHA-1",
    # ),
    body: IngestModelBody = Body(..., description="Metadata of the model (README.md file content)"),
    user: User = Depends(get_current_user),
):
    """
    Ingest file to existing model. 
    """
    try:
        presigned_url = await ingest_model_file(
            body.file_name, model_id, user
        )
        return {
            "presigned_url": presigned_url,
        }
    except Exception as e:
        logger.exception("models:ingest")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

class CompleteIngestionBody(BaseModel):
    version: int
    size: int

@router.post(
    "/complete/{model_id}",
    summary="Complete the ingestion of a model",
    responses=ingest_files_responses,
)
def complete_ingestion(
    model_id: str = Path(..., description="ID of the model"),
    body: CompleteIngestionBody = Body(..., description="Version and size of the model"),
    user: User = Depends(get_current_user),
):
    try:
        complete_model_ingestion(model_id, user, body.version, body.size)
        return {
            "message": "Ingestion completed"
        }
    except Exception as e:
        logger.exception("models:ingest")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))