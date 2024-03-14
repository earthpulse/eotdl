from fastapi.exceptions import HTTPException
from fastapi import APIRouter, status, Depends, Path, Body
import logging
from pydantic import BaseModel
from typing import Optional, List

from ..auth import get_current_user
from ...src.models import User
from ...src.usecases.models import toggle_like_model, update_model
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


@router.put("/{model_id}", summary="Update a model", responses=update_model_responses)
def update(
    model_id: str = Path(..., description="ID of the model"),
    body: UpdateBody = Body(..., description="Metadata of the model"),
    user: User = Depends(get_current_user),
):
    """
    Update a model. A request body must be provided, and must contain the following fields:
    - name: the name of the model.
    - description: a brief description of the model.
    - tags: the tags of the model.
    - authors: the author or authors of the model.
    - license: the license of the model.
    - source: the source of the model.
    - thumbnail: the thumbnail of the model.
    """
    try:
        return update_model(
            model_id,
            user,
            body.name,
            body.authors,
            body.source,
            body.license,
            body.tags,
            body.description,
            body.thumbnail,
        )
    except Exception as e:
        logger.exception("models:ingest")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
