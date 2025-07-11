from fastapi.exceptions import HTTPException
from pydantic import BaseModel
from fastapi import APIRouter, status, Depends, Path, Body
import logging
from typing import List, Optional
import traceback

from ..auth import get_current_user
from ...src.models import User
from ...src.models import Dataset
from ...src.usecases.datasets import update_dataset, toggle_like_dataset, deactivate_dataset, make_dataset_private, allow_user_to_private_dataset, remove_user_from_private_dataset

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


@router.patch("/{dataset_id}/deactivate")
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

class AllowUserRequest(BaseModel):
    email: Optional[str] = None
    user_id: Optional[str] = None

@router.patch("/{dataset_id}/allow-user")
def allow_user(
    dataset_id: str,
    body: AllowUserRequest,
    user: User = Depends(get_current_user),
):
    try:
        message = allow_user_to_private_dataset(dataset_id, user, body.email, body.user_id)
        return {"message": message}
    except Exception as e:
        traceback.print_exc()
        logger.exception("datasets:allow_user")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

@router.patch("/{dataset_id}/remove-user")
def remove_user(
    dataset_id: str,
    body: AllowUserRequest,
    user: User = Depends(get_current_user),
):
    try:
        message = remove_user_from_private_dataset(dataset_id, user, body.email, body.user_id)
        return {"message": message}
    except Exception as e:
        traceback.print_exc()
        logger.exception("datasets:remove_user")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    
@router.patch("/{dataset_id}/make-private")
def make_private(
    dataset_id: str,
    user: User = Depends(get_current_user),
):
    try:
        message = make_dataset_private(dataset_id, user)
        return {"message": message}
    except Exception as e:
        logger.exception("datasets:make_private")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e)
)
