from fastapi.exceptions import HTTPException
from fastapi import APIRouter, status, Depends
import logging

from ..auth import get_current_user, key_auth
from ...src.models import User
from ...src.usecases.datasets import delete_dataset, delete_dataset_file

router = APIRouter()
logger = logging.getLogger(__name__)


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
