from fastapi.exceptions import HTTPException
from fastapi import APIRouter, status, Depends, Path, Body
import logging

from ..auth import get_current_user
from ...src.models import User
from ...src.models import Dataset
from ...src.usecases.datasets import update_dataset, toggle_like_dataset, deactivate_dataset

from .responses import update_dataset_responses

router = APIRouter()
logger = logging.getLogger(__name__)


@router.put("/{id}/like", include_in_schema=False)
def like(
    id: str,
    user: User = Depends(get_current_user),
):
    try:
        return toggle_like_dataset(id, user)
    except Exception as e:
        logger.exception("datasets:like")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.put(
    "/{dataset_id}", summary="Update a dataset", responses=update_dataset_responses
)
def update(
    dataset_id: str = Path(..., description="ID of the dataset"),
    body: Dataset = Body(..., description="Metadata of the dataset"),
    user: User = Depends(get_current_user),
):
    """
    Update a dataset.
    """
    try:
        return update_dataset(
            dataset_id,
            user,
            body,
        )
    except Exception as e:
        logger.exception("datasets:update")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.patch("/deactivate/{dataset_id}")
def deactivate(
    dataset_id: str,
    user: User = Depends(get_current_user),
):
    try:
        message = deactivate_dataset(dataset_id, user)
        return {"message": message}
    except Exception as e:
        logger.exception("datasets:deactivate")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
