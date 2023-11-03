from fastapi.exceptions import HTTPException
from fastapi import APIRouter, status, Depends, File, Form, UploadFile, Path, Query
import logging
from typing import List

from ..auth import get_current_user
from ...src.models import User
from ...src.usecases.models import (
    ingest_model_files_batch,
    add_files_batch_to_model_version,
)
from .responses import ingest_files_responses

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post(
    "/{model_id}/batch",
    summary="Batch ingest files to a model",
    responses=ingest_files_responses,
)
async def ingest_files_batch(
    model_id: str = Path(..., description="ID of the model"),
    version: int = Query(None, description="Version of the model"),
    batch: UploadFile = File(
        ..., description="Batch file (.zip) containing the files to ingest"
    ),
    checksums: List[str] = Form(
        ...,
        description="List of checksums of the files to ingest, calculated with SHA-1",
    ),
    user: User = Depends(get_current_user),
):
    """
    Batch ingest of files to an existing model. The batch file must be a compressed file (.zip).
    The checksums are calculated using the SHA-1 checksums algorithm.
    """
    # try:
    model_id, model_name, filenames = await ingest_model_files_batch(
        batch, model_id, checksums, user, version
    )
    return {
        "model_id": model_id,
        "model_name": model_name,
        "filenames": filenames,
    }
    # except Exception as e:
    #     logger.exception("models:ingest")
    #     raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.post(
    "/{model_id}/files",
    summary="Ingest existing files",
    responses=ingest_files_responses,
)
def ingest_existing_file(
    model_id: str = Path(..., description="ID of the model"),
    version: int = Query(..., description="Version of the model"),
    filenames: List[str] = Form(..., description="Filenames to ingest"),
    checksums: List[str] = Form(
        ..., description="List of checksums of the files to ingest"
    ),
    user: User = Depends(get_current_user),
):
    """
    Ingest a file to an existing model.
    """
    try:
        model_id, model_name, filename = add_files_batch_to_model_version(
            filenames, checksums, model_id, version, user
        )
        return {
            "model_id": model_id,
            "model_name": model_name,
            "filename": filename,
        }
    except Exception as e:
        logger.exception("models:ingest")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


# except Exception as e:
#     logger.exception("models:ingest")
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
#         logger.exception("models:ingest_url")
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
#     #     logger.exception("models:ingest")
#     #     raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
