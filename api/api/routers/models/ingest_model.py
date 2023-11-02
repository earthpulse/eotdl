from fastapi.exceptions import HTTPException
from fastapi import APIRouter, status, Depends, File, Form, UploadFile, Path, Query
import logging
from pydantic import BaseModel
from typing import Optional

from ..auth import get_current_user
from ...src.models import User
from ...src.usecases.models import (
    ingest_model_file,
    ingest_existing_model_file,
)  # , ingest_stac, ingest_file_url
from .responses import ingest_model_responses

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/{model_id}", summary="Ingest a model", responses=ingest_model_responses)
async def ingest(
    model_id: str = Path(..., description="ID of the model"),
    file: Optional[UploadFile] = File(None, description="File to ingest"),
    version: int = Form(..., description="Version of the model to ingest"),  # debería quitarlo (un file solo se puede subir a la última versión si no está ya)
    parent: str = Form(None, description="Parent of the file in the model"),  # debería quitarlo (sacarlo del nombre?)
    checksum: str = Form(None, description="Checksum of the model to ingest, calculated with SHA-1"),  # optional bc browser
    filename: str = Form(None, description="Filename of the model to ingest"),
    fileversion: int = Form(None, description="Version of the file to ingest"),
    user: User = Depends(get_current_user),
):
    """
    Ingest a model to the EOTDL. A file can be optionally provided, in order to ingest an existing file.
    The checksums are calculated using the SHA-1 checksums algorithm.
    """
    # try:
    if filename:
        assert not file, "File provided as both file and filename"
        assert not parent, "Parent provided as both parent and filename"
        assert fileversion, "Fileversion not provided"
        model_id, model_name, file_name = await ingest_existing_model_file(
            filename, model_id, fileversion, version, checksum, user
        )
    else:
        if file.size > 1000000000:  # 1GB
            raise Exception("File too large, please use the CLI to upload large files.")
        model_id, model_name, file_name = await ingest_model_file(
            file, model_id, version, parent, checksum, user
        )
    return {
        "model_id": model_id,
        "model_name": model_name,
        "file_name": file_name,
    }


# except Exception as e:
#     logger.exception("datasets:ingest")
#     raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


# class IngestSTACBody(BaseModel):
#     stac: dict  # json as string


# @router.put("/stac/{model_id}")
# async def ingest_stac_catalog(
#     model_id: str,
#     body: IngestSTACBody,
#     user: User = Depends(get_current_user),
# ):
#     try:
#         return ingest_stac(body.stac, model_id, user)
#     except Exception as e:
#         logger.exception("datasets:ingest_url")
#         raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

# class IngestURLBody(BaseModel):
#     url: str


# @router.post("/{model_id}/url")
# async def ingest_url(
#     model_id: str,
#     body: IngestURLBody,
#     user: User = Depends(get_current_user),
# ):
#     # try:
#     model_id, model_name, file_name = await ingest_file_url(
#         body.url, model_id, user
#     )
#     return {
#         "model_id": model_id,
#         "model_name": model_name,
#         "file_name": file_name,
#     }
#     # except Exception as e:
#     #     logger.exception("datasets:ingest")
#     #     raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
