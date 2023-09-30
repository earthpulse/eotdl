from fastapi.exceptions import HTTPException
from fastapi import APIRouter, status, Depends
import logging

from ..auth import get_current_user
from ...src.models import User
from ...src.usecases.datasets import create_dataset_version

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/version/{dataset_id}")
def version(
    dataset_id: str,
    user: User = Depends(get_current_user),
):
    try:
        version = create_dataset_version(dataset_id, user)
        return {"version": version}
    except Exception as e:
        logger.exception("datasets:version")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))