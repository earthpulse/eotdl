from fastapi.exceptions import HTTPException
from fastapi import APIRouter, status, Depends, Path, Body
import logging
from typing import Optional, List
from pydantic import BaseModel

from ..auth import get_current_user
from ...src.models import User
from ...src.models import Dataset
from ...src.usecases.datasets import toggle_like_dataset, update_dataset
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


class UpdateBody(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    authors: Optional[List[str]] = None
    source: Optional[str] = None
    license: Optional[str] = None


@router.put(
    "/{dataset_id}", summary="Update a dataset", responses=update_dataset_responses
)
def update(
    dataset_id: str = Path(..., description="ID of the dataset"),
    body: UpdateBody = Body(..., description="Metadata of the dataset"),
    user: User = Depends(get_current_user),
):
    """
    Update a dataset. A request body must be provided, and must contain the following fields:
    - name: the name of the dataset.
    - description: a brief description of the dataset.
    - tags: the tags of the dataset.
    - authors: the author or authors of the dataset.
    - license: the license of the dataset.
    - source: the source of the dataset.
    """
    try:
        return update_dataset(
            dataset_id,
            user,
            body.name,
            body.authors,
            body.source,
            body.license,
            body.tags,
            body.description,
        )
    except Exception as e:
        logger.exception("datasets:ingest")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
