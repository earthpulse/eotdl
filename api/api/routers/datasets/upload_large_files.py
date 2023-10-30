from fastapi.exceptions import HTTPException
from fastapi import APIRouter, status, Depends, File, Form, UploadFile
import logging
from pydantic import BaseModel
from typing import Optional

from ..auth import get_current_user
from ...src.models import User
from ...src.usecases.datasets import (
    generate_upload_id,
    ingest_dataset_chunk,
    complete_multipart_upload,
)

router = APIRouter()
logger = logging.getLogger(__name__)


class UploadIdBody(BaseModel):
    filname: str
    checksum: str


@router.post("/{dataset_id}/uploadId", include_in_schema=False)
def start_large_dataset_upload(
    dataset_id: str,
    body: UploadIdBody,
    user: User = Depends(get_current_user),
):
    try:
        upload_id, parts = generate_upload_id(
            user, body.checksum, body.filname, dataset_id
        )
        return {"upload_id": upload_id, "parts": parts}
    except Exception as e:
        logger.exception("datasets:start_large_dataset_upload")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.post("/chunk/{upload_id}", include_in_schema=False)
def ingest_large_dataset_chunk(
    upload_id: str,
    file: UploadFile = File(...),
    part_number: int = Form(...),
    checksum: str = Form(...),
    user: User = Depends(get_current_user),
):
    try:
        message = ingest_dataset_chunk(
            file.file, part_number, upload_id, checksum, user
        )
        return {"message": message}
    except Exception as e:
        logger.exception("datasets:ingest_large_dataset_chunk")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.post("/complete/{upload_id}", include_in_schema=False)
async def complete_large_dataset_upload(
    upload_id: str,
    user: User = Depends(get_current_user),
):
    try:
        dataset = await complete_multipart_upload(user, upload_id)
        return {"dataset": dataset}
    except Exception as e:
        logger.exception("datasets:complete_large_dataset_upload")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
