from fastapi.exceptions import HTTPException
from fastapi import APIRouter, status, Depends, File, Form, UploadFile, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional, Union
import logging

from ..src.models import User
from ..src.usecases.datasets import (
    ingest_file,
    retrieve_datasets,
    retrieve_dataset_by_name,
    retrieve_liked_datasets,
    retrieve_popular_datasets,
    # delete_dataset,
    # ingest_dataset_chunk,
    # like_dataset,
    # download_dataset,
    # edit_dataset,
    # retrieve_datasets_leaderboard,
    # generate_upload_id,
    # complete_multipart_upload,
    # update_dataset,
)
from .auth import get_current_user, key_auth

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/datasets", tags=["datasets"])


@router.post("")
async def ingest(
    file: UploadFile = File(...),
    dataset: str = Form(...),
    checksum: str = Form(...),
    user: User = Depends(get_current_user),
):
    try:
        return await ingest_file(file, dataset, checksum, user)
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


# @router.put("")
# async def update(
#     dataset_id: str = Form(...),
#     file: Optional[Union[UploadFile, None]] = File(None),
#     name: Optional[Union[str, None]] = Form(None),
#     author: Optional[Union[str, None]] = Form(None),
#     link: Optional[Union[str, None]] = Form(None),
#     license: Optional[Union[str, None]] = Form(None),
#     tags: Optional[str] = Form(""),
#     description: Optional[Union[str, None]] = Form(None),
#     user: User = Depends(get_current_user),
# ):
#     try:
#         tags = tags.split(",") if tags != "" else []
#         return await update_dataset(
#             dataset_id, user, file, name, author, link, license, tags, description
#         )
#     except Exception as e:
#         logger.exception("datasets:ingest")
#         raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


# @router.get("/{id}/download/{file}")
# async def download(
#     id: str,
#     file: str,
#     user: User = Depends(get_current_user),
# ):
#     try:
#         data_stream, object_info, name = download_dataset(id, file, user)
#         response_headers = {
#             "Content-Disposition": f'attachment; filename="{name}"',
#             "Content-Type": object_info.content_type,
#             "Content-Length": str(object_info.size),
#         }
#         return StreamingResponse(
#             data_stream(id, file),
#             headers=response_headers,
#             media_type=object_info.content_type,
#         )
#     except Exception as e:
#         logger.exception("datasets:download")
#         raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


# class EditBody(BaseModel):
#     name: Optional[str]
#     description: Optional[str]
#     tags: Optional[List[str]]


# # @router.put("/{id}")
# # def edit(
# #     id: str,
# #     body: EditBody,
# #     user: User = Depends(get_current_user),
# # ):
# #     try:
# #         return edit_dataset(id, body.name, body.description, body.tags, user)
# #     except Exception as e:
# #         logger.exception("datasets:edit")
# #         raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


# @router.put("/{id}/like", include_in_schema=False)
# def like(
#     id: str,
#     user: User = Depends(get_current_user),
# ):
#     try:
#         return like_dataset(id, user)
#     except Exception as e:
#         logger.exception("datasets:like")
#         raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


# @router.get("/leaderboard", include_in_schema=False)
# def leaderboard():
#     try:
#         return retrieve_datasets_leaderboard()
#     except Exception as e:
#         logger.exception("datasets:leaderboard")
#         raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


# @router.delete("/{name}", include_in_schema=False)
# def delete(
#     name: str,
#     isAdmin: bool = Depends(key_auth),
# ):
#     try:
#         return delete_dataset(name)
#     except Exception as e:
#         logger.exception("datasets:delete")
#         raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


# class UploadIdBody(BaseModel):
#     name: str
#     dataset: str
#     checksum: str


# @router.post("/uploadId", include_in_schema=False)
# def start_large_dataset_upload(
#     body: UploadIdBody,
#     user: User = Depends(get_current_user),
# ):
#     # try:
#     upload_id, parts = generate_upload_id(user, body.checksum, body.name, body.dataset)
#     return {"upload_id": upload_id, "parts": parts}
#     # except Exception as e:
#     #     logger.exception("datasets:start_large_dataset_upload")
#     #     raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


# # @router.get("/chunk/{id}", include_in_schema=False)
# # def start_large_dataset_update(
# #     id: str,
# #     checksum: str,
# #     user: User = Depends(get_current_user),
# # ):
# #     try:
# #         dataset_id, upload_id, parts = generate_upload_id(user, checksum, id=id)
# #         return {"dataset_id": dataset_id, "upload_id": upload_id, "parts": parts}
# #     except Exception as e:
# #         logger.exception("datasets:start_large_dataset_update")
# #         raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


# @router.post("/chunk/{upload_id}", include_in_schema=False)
# def ingest_large_dataset_chunk(
#     upload_id: str,
#     file: UploadFile = File(...),
#     part_number: int = Form(...),
#     checksum: str = Form(...),
#     user: User = Depends(get_current_user),
# ):
#     try:
#         message = ingest_dataset_chunk(
#             file.file, part_number, upload_id, checksum, user
#         )
#         return {"message": message}
#     except Exception as e:
#         logger.exception("datasets:ingest_large_dataset_chunk")
#         raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


# class CompleteBody(BaseModel):
#     name: Optional[str]
#     description: Optional[str]
#     checksum: str


# @router.post("/complete/{upload_id}", include_in_schema=False)
# async def complete_large_dataset_upload(
#     upload_id: str,
#     user: User = Depends(get_current_user),
# ):
#     # try:
#     dataset = await complete_multipart_upload(user, upload_id)
#     return {"dataset": dataset}
#     # except Exception as e:
#     #     logger.exception("datasets:complete_large_dataset_upload")
#     #     raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
