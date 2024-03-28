from fastapi.exceptions import HTTPException
from fastapi import APIRouter, status, Depends, File, Form, UploadFile, Path, Query
import logging
from pydantic import BaseModel
from typing import Optional, List

from ..auth import get_current_user
from ...src.models import User
from ...src.usecases.datasets import (
    ingest_dataset_file,
    ingest_dataset_files_batch,
    add_files_batch_to_dataset_version,
    ingest_stac,
)
from .responses import ingest_files_responses

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post(
    "/{dataset_id}",
    summary="Ingest file to a dataset",
    responses=ingest_files_responses,
)
async def ingest_files(
    dataset_id: str = Path(..., description="ID of the dataset"),
    version: int = Query(None, description="Version of the dataset"),
    file: UploadFile = File(
        ..., description="Batch file (.zip) containing the files to ingest"
    ),
    checksum: str = Form(
        ...,
        description="checksums of the files to ingest, calculated with SHA-1",
    ),
    user: User = Depends(get_current_user),
):
    """
    Batch ingest of files to an existing dataset. The batch file must be a compressed file (.zip).
    The checksums are calculated using the SHA-1 checksums algorithm.
    """
    try:
        dataset_id, dataset_name, filename = await ingest_dataset_file(
            file, dataset_id, checksum, user, version
        )
        return {
            "dataset_id": dataset_id,
            "dataset_name": dataset_name,
            "filename": filename,
        }
    except Exception as e:
        logger.exception("datasets:ingest")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.post(
    "/{dataset_id}/batch",
    summary="Batch ingest files to a dataset",
    responses=ingest_files_responses,
)
async def ingest_files_batch(
    dataset_id: str = Path(..., description="ID of the dataset"),
    version: int = Query(None, description="Version of the dataset"),
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
    Batch ingest of files to an existing dataset. The batch file must be a compressed file (.zip).
    The checksums are calculated using the SHA-1 checksums algorithm.
    """
    try:
        dataset_id, dataset_name, filenames = await ingest_dataset_files_batch(
            batch, dataset_id, checksums, user, version
        )
        return {
            "dataset_id": dataset_id,
            "dataset_name": dataset_name,
            "filenames": filenames,
        }
    except Exception as e:
        logger.exception("datasets:ingest")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.post(
    "/{dataset_id}/files",
    summary="Ingest existing files",
    responses=ingest_files_responses,
)
def ingest_existing_file(
    dataset_id: str = Path(..., description="ID of the dataset"),
    version: int = Query(..., description="Version of the dataset"),
    filenames: List[str] = Form(..., description="Filenames to ingest"),
    checksums: List[str] = Form(
        ..., description="List of checksums of the files to ingest"
    ),
    user: User = Depends(get_current_user),
):
    """
    Ingest a file to an existing dataset.
    """
    try:
        dataset_id, dataset_name, filename = add_files_batch_to_dataset_version(
            filenames, checksums, dataset_id, version, user
        )
        return {
            "dataset_id": dataset_id,
            "dataset_name": dataset_name,
            "filename": filename,
        }
    except Exception as e:
        logger.exception("datasets:ingest")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


class IngestSTACBody(BaseModel):
    stac: dict  # json as string


@router.put("/stac/{dataset_id}")
def ingest_stac_catalog(
    dataset_id: str,
    body: IngestSTACBody,
    user: User = Depends(get_current_user),
):
    try:
        return ingest_stac(body.stac, dataset_id, user)
    except Exception as e:
        logger.exception("datasets:ingest_url")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))