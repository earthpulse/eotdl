from fastapi.exceptions import HTTPException
from fastapi import APIRouter, status, Depends
import logging
from fastapi.responses import StreamingResponse

from ..auth import get_current_user
from ...src.models import User
from ...src.usecases.datasets import download_dataset_file  # , download_stac_catalog

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/{dataset_id}/download/{filename}")
async def download_dataset(
    dataset_id: str,
    filename: str,  # podría ser un path... a/b/c/file.txt
    version: int = None,
    user: User = Depends(get_current_user),
):
    print(filename)
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


# @router.get("/{dataset_id}/download")
# async def download_stac_Catalog(
#     dataset_id: str,
#     user: User = Depends(get_current_user),
# ):
#     try:
#         return download_stac_catalog(dataset_id, user)
#     except Exception as e:
#         logger.exception("datasets:download")
#         raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
