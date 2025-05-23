from fastapi.exceptions import HTTPException
from fastapi import APIRouter, status, Depends, Body, File, Form, UploadFile, Path, Query
import logging
from pydantic import BaseModel
from typing import Optional, List
import traceback

from ..auth import get_current_user
from ...src.models import User
from ...src.usecases.datasets import (
    ingest_dataset_file,
    complete_dataset_ingestion
)
from .responses import ingest_files_responses

router = APIRouter()
logger = logging.getLogger(__name__)

class IngestDatasetBody(BaseModel):
    file_name: str

@router.post(
    "/{dataset_id}",
    summary="Ingest file to a dataset",
    responses=ingest_files_responses,
)
async def ingest_files(
    dataset_id: str = Path(..., description="ID of the dataset"),
    # version: int = Query(None, description="Version of the dataset"),
    # file: UploadFile = File(
    #     ..., description="file to ingest"
    # ),
    # checksum: str = Form(
    #     ...,
    #     description="checksum of the file to ingest, calculated with SHA-1",
    # ),
    body: IngestDatasetBody = Body(..., description="Metadata of the dataset (README.md file content)"),
    user: User = Depends(get_current_user),
):
    """
     Ingest file to existing dataset.
    """
    try:
        presigned_url = await ingest_dataset_file(
            body.file_name, dataset_id, user
        )
        return {
            "presigned_url": presigned_url,
        }
    except Exception as e:
        logger.exception("datasets:ingest")
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

class CompleteIngestionBody(BaseModel):
    version: int
    size: int

@router.post(
    "/complete/{dataset_id}",
    summary="Complete the ingestion of a dataset",
    responses=ingest_files_responses,
)
def complete_ingestion(
    dataset_id: str = Path(..., description="ID of the dataset"),
    body: CompleteIngestionBody = Body(..., description="Version and size of the dataset"),
    user: User = Depends(get_current_user),
):
    try:
        complete_dataset_ingestion(dataset_id, user, body.version, body.size)
        return {
            "message": "Ingestion completed"
        }
    except Exception as e:
        logger.exception("datasets:ingest")
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))