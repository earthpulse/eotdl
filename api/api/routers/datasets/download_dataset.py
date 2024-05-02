from fastapi.exceptions import HTTPException
from fastapi import APIRouter, status, Depends, Query, Path
import logging
from fastapi.responses import StreamingResponse

from ..auth import get_current_user
from ...src.models import User
from ...src.usecases.datasets import download_dataset_file, download_stac_catalog, generate_presigned_url
from .responses import download_dataset_responses as responses

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get(
    "/{dataset_id}/download/{filename:path}",
    summary="Download a dataset",
    responses=responses,
)
async def download_dataset(
    dataset_id: str = Path(..., description="ID of the dataset to download"),
    filename: str = Path(
        ..., description="Filename or path to the file to download from the dataset"
    ),  # podría ser un path... a/b/c/file.txt
    version: int = Query(None, description="Version of the dataset to download"),
    user: User = Depends(get_current_user),
):
    """
    Download an entire dataset or a specific dataset file from the EOTDL.
    """
    try:
        data_stream, object_info, _filename = download_dataset_file(
            dataset_id, filename, user, version
        )
        response_headers = {
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Type": object_info.content_type,
            "Content-Length": str(object_info.size),
        }
        return StreamingResponse(
            data_stream(dataset_id, _filename),
            headers=response_headers,
            media_type=object_info.content_type,
        )
    except Exception as e:
        logger.exception("datasets:download")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.get("/{dataset_id}/download")
async def download_stac_Catalog(
    dataset_id: str,
    user: User = Depends(get_current_user),
):
    try:
        return download_stac_catalog(dataset_id, user)
    except Exception as e:
        logger.exception("datasets:download")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


# @router.get(
#     "/{dataset_id}/url/{filename:path}",
#     summary="Retrieve a presigend get url",
#     responses=responses,
# )
# async def generate_a_presigned_url(
#     dataset_id: str = Path(..., description="ID of the dataset to download"),
#     filename: str = Path(
#         ..., description="Filename or path to the file to download from the dataset"
#     ),  # podría ser un path... a/b/c/file.txt
#     version: int = Query(None, description="Version of the dataset to download"),
#     user: User = Depends(get_current_user),
# ):
#     try:
#         return generate_presigned_url(dataset_id, filename, version)
#     except Exception as e:
#         logger.exception("datasets:download")
#         raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))