from fastapi.exceptions import HTTPException
from fastapi import APIRouter, status, Depends, File, Form, UploadFile, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional, Union
import logging
import json

from ..src.models import User
from ..src.usecases.datasets import (
    ingest_file,
    ingest_file_url,
    ingest_stac,
    create_dataset,
    retrieve_datasets,
    retrieve_dataset_by_name,
    retrieve_liked_datasets,
    retrieve_popular_datasets,
    like_dataset,
    retrieve_datasets_leaderboard,
    generate_upload_id,
    ingest_dataset_chunk,
    complete_multipart_upload,
    download_dataset,
    update_dataset,
    delete_dataset,
    download_stac,
    delete_dataset_file,
)
from .auth import get_current_user, key_auth

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/datasets", tags=["datasets"])


# class IngestSTACBody(BaseModel):
#     stac: dict  # json as string
#     dataset: str


# @router.post("/stac")
# async def ingest_stac_catalog(
#     body: IngestSTACBody,
#     user: User = Depends(get_current_user),
# ):
#     # try:
#     # stac = json.loads(body.stac)
#     return ingest_stac(body.stac, body.dataset, user)
#     # except Exception as e:
#     #     logger.exception("datasets:ingest_url")
#     #     raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


class CreateDatasetBody(BaseModel):
    name: str
    authors: List[str]
    source: str
    license: str


@router.post("")
def create(
    metadata: CreateDatasetBody,
    user: User = Depends(get_current_user),
):
    try:
        dataset_id = create_dataset(
            user, metadata.name, metadata.authors, metadata.source, metadata.license
        )
        return {"dataset_id": dataset_id}
    except Exception as e:
        logger.exception("datasets:ingest")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.post("/{dataset_id}")
async def ingest(
    dataset_id: str,
    file: UploadFile = File(...),
    # optional since from browser cannot compute checksum easily
    checksum: str = Form(None),
    user: User = Depends(get_current_user),
):
    try:
        if file.size > 1000000000:  # 1GB
            raise Exception("File too large, please use the CLI to upload large files.")
        dataset_id, dataset_name, file_name = await ingest_file(
            file, dataset_id, checksum, user
        )
        return {
            "dataset_id": dataset_id,
            "dataset_name": dataset_name,
            "file_name": file_name,
        }
    except Exception as e:
        logger.exception("datasets:ingest")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


class IngestURLBody(BaseModel):
    url: str
    dataset: str


# @router.post("/url")
# async def ingest_url(
#     body: IngestURLBody,
#     user: User = Depends(get_current_user),
# ):
#     try:
#         dataset_id, dataset_name, file_name = await ingest_file_url(
#             body.url, body.dataset, user
#         )
#         return {
#             "dataset_id": dataset_id,
#             "dataset_name": dataset_name,
#             "file_name": file_name,
#         }
#     except Exception as e:
#         logger.exception("datasets:ingest")
#         raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


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


class UploadIdBody(BaseModel):
    name: str
    checksum: str


@router.post("/{dataset_id}/uploadId", include_in_schema=False)
def start_large_dataset_upload(
    dataset_id: str,
    body: UploadIdBody,
    user: User = Depends(get_current_user),
):
    try:
        upload_id, parts = generate_upload_id(
            user, body.checksum, body.name, dataset_id
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


class CompleteBody(BaseModel):
    name: Optional[str]
    description: Optional[str]
    checksum: str


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


@router.get("/{id}/download/{file}")
async def download(
    id: str,
    file: str,
    user: User = Depends(get_current_user),
):
    try:
        data_stream, object_info, name = download_dataset(id, file, user)
        response_headers = {
            "Content-Disposition": f'attachment; filename="{name}"',
            "Content-Type": object_info.content_type,
            "Content-Length": str(object_info.size),
        }
        return StreamingResponse(
            data_stream(id, file),
            headers=response_headers,
            media_type=object_info.content_type,
        )
    except Exception as e:
        logger.exception("datasets:download")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


# @router.get("/{id}/download")
# async def download(
#     id: str,
#     user: User = Depends(get_current_user),
# ):
#     try:
#         return download_stac(id, user)
#     except Exception as e:
#         logger.exception("datasets:download")
#         raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


class UpdateBody(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    authors: Optional[List[str]] = None
    source: Optional[str] = None
    license: Optional[str] = None


@router.put("/{id}")
def update(
    id: str,
    body: UpdateBody,
    user: User = Depends(get_current_user),
):
    try:
        return update_dataset(
            id,
            user,
            body.name,
            body.authors,
            body.source,
            body.license,
            body.tags,
            body.description,
        )
    except Exception as e:
        logger.exception("datasets:ingest")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.delete("/{name}", include_in_schema=False)
def delete(
    name: str,
    isAdmin: bool = Depends(key_auth),
):
    try:
        message = delete_dataset(name)
        return {"message": message}
    except Exception as e:
        logger.exception("datasets:delete")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.delete("/{dataset_id}/file/{file_name}")
def delete(
    dataset_id: str,
    file_name: str,
    user: User = Depends(get_current_user),
):
    try:
        message = delete_dataset_file(user, dataset_id, file_name)
        return {"message": message}
    except Exception as e:
        logger.exception("datasets:delete")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
