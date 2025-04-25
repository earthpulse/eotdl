from fastapi.exceptions import HTTPException
from fastapi import APIRouter, status, Depends, Path, Body
import logging
from pydantic import BaseModel
from typing import Optional, List
import traceback

from ..auth import get_current_user
from ...src.models import User, Model
from ...src.usecases.models import update_model, toggle_like_model, deactivate_model, private_models

from .responses import update_model_responses

router = APIRouter()
logger = logging.getLogger(__name__)


@router.put("/{id}/like", include_in_schema=False)
def like(
    id: str,
    user: User = Depends(get_current_user),
):
    try:
        return toggle_like_model(id, user)
    except Exception as e:
        logger.exception("models:like")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


class UpdateBody(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    authors: Optional[List[str]] = None
    source: Optional[str] = None
    license: Optional[str] = None
    thumbnail: Optional[str] = None


@router.put(
    "/{model_id}", summary="Update a model", responses=update_model_responses
)
def update(
    model_id: str = Path(..., description="ID of the model"),
    body: Model = Body(..., description="Metadata of the model"),
    user: User = Depends(get_current_user),
):
    """
    Update a model.
    """
    try:
        return update_model(
            model_id,
            user,
            body,
        )
    except Exception as e:  
        print(traceback.format_exc())
        logger.exception("models:update")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.patch("/{model_id}/deactivate", include_in_schema=False)
def deactivate(
    model_id: str,
    user: User = Depends(get_current_user),
):
    try:
        message = deactivate_model(model_id, user)
        return {"message": message}
    except Exception as e:
        logger.exception("models:deactivate")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

@router.patch("/{model_id}/allow-user/{user_id}")
def allow_user(
    dataset_id: str,
    user_id: str,
    user: User = Depends(get_current_user),
):
    try:
        message = private_models.allow_user_to_private_model(dataset_id, user, user_id)
        return {"message": message}
    except Exception as e:
        logger.exception("models:allow_user")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.patch("/{model_id}/make-private")
def make_private(
    dataset_id: str,
    user: User = Depends(get_current_user),
):
    try:
        message = private_models.make_model_private(dataset_id, user)
        return {"message": message}
    except Exception as e:
        logger.exception("models:make_private")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e)
)

