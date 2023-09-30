from fastapi.exceptions import HTTPException
from fastapi import APIRouter, status, Depends
import logging
from fastapi.responses import StreamingResponse

from ..auth import get_current_user
from ...src.models import User
from ...src.usecases.datasets import download_dataset, download_stac

router = APIRouter()
logger = logging.getLogger(__name__)

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


@router.get("/{id}/download")
async def download(
    id: str,
    user: User = Depends(get_current_user),
):
    try:
        return download_stac(id, user)
    except Exception as e:
        logger.exception("datasets:download")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))