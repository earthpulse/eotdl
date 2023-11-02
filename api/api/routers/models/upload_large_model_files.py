from fastapi.exceptions import HTTPException
from fastapi import APIRouter, status, Depends, File, Form, UploadFile
import logging
from pydantic import BaseModel

from ..auth import get_current_user
from ...src.models import User
from ...src.usecases.models import (
    generate_upload_id,
    ingest_model_chunk,
    complete_multipart_upload,
)

router = APIRouter()
logger = logging.getLogger(__name__)


class UploadIdBody(BaseModel):
    filname: str
    checksum: str


@router.post("/{model_id}/uploadId", include_in_schema=False)
def start_large_model_upload(
    model_id: str,
    body: UploadIdBody,
    user: User = Depends(get_current_user),
):
    try:
        upload_id, parts = generate_upload_id(
            user, body.checksum, body.filname, model_id
        )
        return {"upload_id": upload_id, "parts": parts}
    except Exception as e:
        logger.exception("models:start_large_model_upload")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.post("/chunk/{upload_id}", include_in_schema=False)
def ingest_large_model_chunk(
    upload_id: str,
    file: UploadFile = File(...),
    part_number: int = Form(...),
    checksum: str = Form(...),
    user: User = Depends(get_current_user),
):
    try:
        message = ingest_model_chunk(file.file, part_number, upload_id, checksum, user)
        return {"message": message}
    except Exception as e:
        logger.exception("models:ingest_large_model_chunk")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.post("/complete/{upload_id}", include_in_schema=False)
async def complete_large_model_upload(
    upload_id: str,
    version: int,
    user: User = Depends(get_current_user),
):
    try:
        model = await complete_multipart_upload(user, upload_id, version)
        return {"model": model}
    except Exception as e:
        logger.exception("models:complete_large_model_upload")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
