from fastapi.exceptions import HTTPException
from fastapi import APIRouter, status, Depends, Path, Query
import logging
from fastapi.responses import StreamingResponse

from ..auth import get_current_user
from ...src.models import User
from ...src.usecases.models import download_model_file, download_stac_catalog
from .responses import download_model_responses

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get(
    "/{model_id}/download/{filename:path}",
    summary="Download a model",
    responses=download_model_responses,
)
async def download_model(
    model_id: str = Path(..., description="ID of the model to download"),
    filename: str = Path(
        ..., description="Filename or path to the file to download from the model"
    ),  # podría ser un path... a/b/c/file.txt
    version: int = Query(None, description="Version of the model to download"),
    user: User = Depends(get_current_user),
):
    """
    Download an entire model or a specific model file from the EOTDL.
    """
    # try:
    data_stream, object_info, _filename = download_model_file(
        model_id, filename, user, version
    )
    response_headers = {
        "Content-Disposition": f'attachment; filename="{filename}"',
        "Content-Type": object_info.content_type,
        "Content-Length": str(object_info.size),
    }
    return StreamingResponse(
        data_stream(model_id, _filename),
        headers=response_headers,
        media_type=object_info.content_type,
    )
    # except Exception as e:
    #     logger.exception("models:download")
    #     raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.get("/{model_id}/download")
async def download_stac_Catalog(
    model_id: str,
    user: User = Depends(get_current_user),
):
    try:
        return download_stac_catalog(model_id, user)
    except Exception as e:
        logger.exception("models:download")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
