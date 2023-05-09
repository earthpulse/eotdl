from fastapi.exceptions import HTTPException
from fastapi import APIRouter, status, Depends, File, Form, UploadFile, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional, Union
import logging

from ..src.models import User
from ..src.usecases.datasets import (
    delete_dataset,
    ingest_dataset_chunk,
    retrieve_liked_datasets,
    like_dataset,
    ingest_dataset,
    retrieve_datasets,
    retrieve_popular_datasets,
    retrieve_dataset_by_name,
    download_dataset,
    edit_dataset,
    retrieve_datasets_leaderboard,
    generate_upload_id,
    complete_multipart_upload,
)
from .auth import get_current_user, key_auth

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/datasets", tags=["datasets"])


@router.post("")
def ingest(
    file: UploadFile = File(...),
    name: str = Form(...),
    description: str = Form(...),
    user: User = Depends(get_current_user),
):
    # if file.size > 1000000000: # 1 GB
    #     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File size too large, the maximum allowed is 1 GB. For larger dataset get in touch with us.")
    try:
        return ingest_dataset(file, name, description, user)
    except Exception as e:
        logger.exception("datasets:ingest")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.get("")
def retrieve(name: str = None, limit: Union[int, None] = None):
    try:
        if name is None:
            return retrieve_datasets(limit)
        return retrieve_dataset_by_name(name)
    except Exception as e:
        logger.exception("datasets:retrieve")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.get("/liked", include_in_schema=False)
def retrieve_liked(
    user: User = Depends(get_current_user),
):
    try:
        return retrieve_liked_datasets(user)
    except Exception as e:
        logger.exception("datasets:retrieve_liked")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.get("/popular", include_in_schema=False)
def retrieve_popular(limit: Union[int, None] = None):
    try:
        return retrieve_popular_datasets(limit)
    except Exception as e:
        logger.exception("datasets:retrieve_popular")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.get("/{id}/download")
async def download(
    id: str,
    user: User = Depends(get_current_user),
):
    try:
        data_stream, object_info, name = download_dataset(id, user)
        response_headers = {
            "Content-Disposition": f'attachment; filename="{name}.zip"',
            "Content-Type": "application/zip",
            "Content-Length": str(object_info.size),
        }
        return StreamingResponse(
            data_stream(id),
            headers=response_headers,
            media_type=object_info.content_type,
        )
    except Exception as e:
        logger.exception("datasets:download")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


class EditBody(BaseModel):
    name: Optional[str]
    description: Optional[str]
    tags: Optional[List[str]]


@router.put("/{id}")
def edit(
    id: str,
    body: EditBody,
    user: User = Depends(get_current_user),
):
    try:
        return edit_dataset(id, body.name, body.description, body.tags, user)
    except Exception as e:
        logger.exception("datasets:edit")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.put("/{id}/like", include_in_schema=False)
def like(
    id: str,
    user: User = Depends(get_current_user),
):
    try:
        return like_dataset(id, user)
    except Exception as e:
        logger.exception("datasets:like")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.get("/leaderboard", include_in_schema=False)
def leaderboard():
    try:
        return retrieve_datasets_leaderboard()
    except Exception as e:
        logger.exception("datasets:leaderboard")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.delete("/{name}", include_in_schema=False)
def delete(
    name: str,
    isAdmin: bool = Depends(key_auth),
):
    try:
        return delete_dataset(name)
    except Exception as e:
        logger.exception("datasets:delete")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.get("/chunk", include_in_schema=True)
def start_large_dataset_upload(
    name: str,
    description: str,
    user: User = Depends(get_current_user),
):
    try:
        dataset_id, upload_id = generate_upload_id(
            name,
            description,
            user,
        )
        return {"dataset_id": dataset_id, "upload_id": upload_id}
    except Exception as e:
        print(str(e))
        logger.exception("datasets:upload_id")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.post("/chunk", include_in_schema=True)
def ingest_large_dataset_chunk(
    request: Request,
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
):
    try:
        upload_id = request.headers.get("upload-id", None)
        part_number = int(request.headers.get("part-number", None))
        dataset_id = request.headers.get("dataset-id", None)
        ingest_dataset_chunk(
            file.file,
            part_number,
            dataset_id,
            upload_id,
        )
        return {"message": "done"}
    except Exception as e:
        logger.exception("datasets:ingest_large")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


class CompleteBody(BaseModel):
    name: str
    description: str


@router.post("/complete", include_in_schema=True)
def complete_large_dataset_upload(
    request: Request,
    body: CompleteBody,
    user: User = Depends(get_current_user),
):
    try:
        upload_id = request.headers.get("upload-id", None)
        dataset_id = request.headers.get("dataset-id", None)
        dataset = complete_multipart_upload(
            user, body.name, body.description, dataset_id, upload_id
        )
        return {"dataset": dataset}
    except Exception as e:
        logger.exception("datasets:ingest_large")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
